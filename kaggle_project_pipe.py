cat_col_to_impute = df.columns[(df.dtypes == 'object') & (df.isna().sum() > 0)]
cat_col_to_impute

num_col_to_impute = df.columns[((df.dtypes == 'int64') | (df.dtypes == 'float64')) & (df.isna().sum() > 0)]
num_col_to_impute

imputer1 = SimpleImputer(strategy = 'most_frequent')
imputer2 = SimpleImputer(strategy = 'median')

cat_imputed = imputer1.fit_transform(df[cat_col_to_impute])
cat_imputed_df = pd.DataFrame(cat_imputed, columns=cat_col_to_impute)
df[cat_col_to_impute] = cat_imputed_df

num_imputed = imputer2.fit_transform(df[num_col_to_impute])
num_imputed_df = pd.DataFrame(num_imputed, columns=num_col_to_impute)
df[num_col_to_impute] = num_imputed_df

df = df.drop(columns=['MachineID','SignatureVersion','IsBetaUser', 
                      'AutoSampleSubmissionEnabled', 'IsFlightsDisabled'])

cat_col = df.columns[(df.dtypes == 'object')].drop(['DateAS', 'DateOS'], errors='ignore')

df[cat_col] = df[cat_col].astype(str)

# Convert to datetime, handling errors
X['DateAS'] = pd.to_datetime(X['DateAS'], errors='coerce')
X['DateOS'] = pd.to_datetime(X['DateOS'], errors='coerce')

# Create new feature for days since OS install
X['Days_Since_OS_Install'] = (X['DateAS'] - X['DateOS']).dt.days

# Drop the original date columns
X = X.drop(['DateAS', 'DateOS'], axis=1)

X['Display_Area'] = X['PrimaryDisplayResolutionHorizontal'] * X['PrimaryDisplayResolutionVertical']

X['RAM_per_Core'] = X['TotalPhysicalRAMMB'] / X['ProcessorCoreCount']

X = X.drop(['PrimaryDisplayResolutionHorizontal','PrimaryDisplayResolutionVertical',
            'TotalPhysicalRAMMB','ProcessorCoreCount'],axis=1)

from sklearn.preprocessing import MinMaxScaler

numerical_columns = X.select_dtypes(include=['float64', 'int64']).columns.tolist()
numerical_columns.remove('target')

scaler = MinMaxScaler()

X[numerical_columns] = scaler.fit_transform(X[numerical_columns])

print("Final shape after scaling:", X.shape)

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder

# Define columns to encode
encode_top_5_values = ['EngineVersion', 'AppVersion', 'OsPlatformSubRelease', 'OSBuildLab',
                       'MDC2FormFactor', 'ChassisType', 'NumericOSVersion', 'OSBranch', 'OSInstallType']
encode_top_3_values = ['OSVersion', 'PowerPlatformRole', 'OSEdition', 'OSSkuFriendlyName',
                       'AutoUpdateOptionsName']
encode_top_2_values = ['PlatformType', 'SKUEditionName', 'PrimaryDiskType', 'LicenseActivationChannel',
                       'FlightRing']
encode_all = ['ProductName', 'Processor', 'DeviceFamily', 'OSArchitecture', 'OSGenuineState']

# Create transformers for the specified columns
transformers = []

# For columns that need all values encoded
for col in encode_all:
    # Get all unique values for the column
    unique_values = X[col].unique()
    transformers.append((
        f'ohe_all_{col}', 
        OneHotEncoder(sparse_output=False, drop='first', handle_unknown='ignore'), 
        [col]
    ))

# For columns with top 5 values
for col in encode_top_5_values:
    top_5_categories = X[col].value_counts().nlargest(5).index.tolist()
    X.loc[~X[col].isin(top_5_categories), col] = 'Other'
    transformers.append((
        f'ohe_top_5_{col}', 
        OneHotEncoder(sparse_output=False, drop='first', handle_unknown='ignore'), 
        [col]
    ))

# For columns with top 3 values
for col in encode_top_3_values:
    top_3_categories = X[col].value_counts().nlargest(3).index.tolist()
    X.loc[~X[col].isin(top_3_categories), col] = 'Other'
    transformers.append((
        f'ohe_top_3_{col}', 
        OneHotEncoder(sparse_output=False, drop='first', handle_unknown='ignore'), 
        [col]
    ))

# For columns with top 2 values
for col in encode_top_2_values:
    top_2_categories = X[col].value_counts().nlargest(2).index.tolist()
    X.loc[~X[col].isin(top_2_categories), col] = 'Other'
    transformers.append((
        f'ohe_top_2_{col}', 
        OneHotEncoder(sparse_output=False, drop='first', handle_unknown='ignore'), 
        [col]
    ))

# Create the ColumnTransformer
preprocessor = ColumnTransformer(transformers)

# Fit and transform the data
X_transformed = preprocessor.fit_transform(X)

# Get feature names
feature_names = preprocessor.get_feature_names_out()

# Convert the transformed data back to a DataFrame
transformed_df = pd.DataFrame(X_transformed, columns=feature_names)

# Drop the original columns that were encoded
columns_to_drop = encode_all + encode_top_5_values + encode_top_3_values + encode_top_2_values
X = X.drop(columns=columns_to_drop).join(transformed_df)

from sklearn.ensemble import IsolationForest

iso_forest = IsolationForest(contamination=0.01)

iso_forest.fit(X)
X['outlier'] = iso_forest.predict(X)

X_cleaned = X[X['outlier'] == 1].drop(columns=['outlier'])

X_cleaned.head()

X_cleaned = X_cleaned.drop_duplicates()

X_cleaned.shape