import pandas as pd
import scipy.stats
import geopandas as gpd

data = pd.read_excel('data.xlsx', sheet_name='Arkusz1')
data = data.iloc[0:36, :]

# One value is missing, I will replace it with mean value
data.loc[22, 'Hospital beds per 10k inhabitants'] = None
data.loc[22, 'Hospital beds per 10k inhabitants'] = data['Hospital beds per 10k inhabitants'].mean()

data['Revenue'] = data['Income'] - data['Expenses']
pvals = []
cols = data.columns[2:]
for c in cols:
    pvals.append(scipy.stats.shapiro(data[c]).pvalue)
print(pvals)
# Not all normally distributed
# min max scaling

for c in cols:
    min_val = data[c].min()
    max_val = data[c].max()
    data[c] = (data[c] - min_val) / (max_val - min_val)

data['Entity per inhabitants indicator'] = 1 - data['Population per 1 healthcare entity']
data['Health'] = (data['Hospital beds per 10k inhabitants'] + data['Entity per inhabitants indicator']) / 2
data['Indicator'] = (data['Population in k'] + data['Health'] + data['Books loans per 1k inhabitants'] + data[
    'Revenue']) / 4

data = data.sort_values(by=['ID'])
counties = gpd.read_file("data/better_sil2.shp")
counties['Score'] = data['Indicator']
counties.to_file("better_sil2.shp")
