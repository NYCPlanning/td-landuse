import geopandas as gpd
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.io as pio
from sklearn.cluster import KMeans

pd.set_option('display.max_columns', None)
path='C:/Users/mayij/Desktop/DOC/DCP2021/LAND USE MIX/'
pio.renderers.default = 'browser'



df=gpd.read_file(path+'mappluto.shp')
df.crs=4326
df=df.to_crs(6539)
df['county']=df['Borough'].map({'BX':'36005','BK':'36047','MN':'36061','QN':'36081','SI':'36085'})
df['tract']=pd.to_numeric(df['CT2010'])
df=df[pd.notna(df['tract'])].reset_index(drop=True)
df['tract']=[str(int(x*100)).zfill(6) for x in df['tract']]
df['tractid']=df['county']+df['tract']
df['land']=[x.area for x in df['geometry']]
df['bldg']=df['ResArea']+df['OfficeArea']+df['RetailArea']+df['GarageArea']+df['StrgeArea']+df['FactryArea']+df['OtherArea']
df=df[df['bldg']!=0].reset_index(drop=True)
df['ttfar']=df['ResidFAR']+df['CommFAR']+df['FacilFAR']
df['btfar']=df['bldg']/df['land']
df=df[df['btfar']<=40].reset_index(drop=True)
df['res']=df['ResArea'].copy()
df['offret']=df['OfficeArea']+df['RetailArea']
df['other']=df['GarageArea']+df['StrgeArea']+df['FactryArea']+df['OtherArea']
df=df.groupby(['tractid'],as_index=False).agg({'res':'sum','offret':'sum','other':'sum','bldg':'sum','land':'sum'}).reset_index(drop=True)
ct=gpd.read_file(path+'nycctclipped.shp')
ct.crs=4326
df=pd.merge(ct,df,how='inner',on='tractid')
df.to_file(path+'ctlu.shp')





df=gpd.read_file(path+'ctlu.shp')
df.crs=4326
df['resfar']=df['res']/df['land']
df['offretfar']=df['offret']/df['land']
df['otherfar']=df['other']/df['land']
k=3 # Elbow
km=KMeans(n_clusters=k)
y=km.fit_predict(df[['resfar','offretfar','otherfar']])
df['farcluster']=y+1
df['respct']=df['res']/df['bldg']
df['offretpct']=df['offret']/df['bldg']
df['otherpct']=df['other']/df['bldg']
k=3 # Elbow
km=KMeans(n_clusters=k)
y=km.fit_predict(df[['respct','offretpct','otherpct']])
df['pctcluster']=y+1
df.to_file(path+'ctlucluster.shp')


p=go.Figure()






df=gpd.read_file(path+'ctlucluster.shp')
df.crs=4326
df['resnum']=np.where(df['res']>0,1,0)
df['offretnum']=np.where(df['offret']>0,1,0)
df['othernum']=np.where(df['other']>0,1,0)
df['lumnum']=df['resnum']+df['offretnum']+df['othernum']
df['reslog']=np.where(df['res']>0,np.log(df['respct']),0)
df['offretlog']=np.where(df['offret']>0,np.log(df['offretpct']),0)
df['otherlog']=np.where(df['other']>0,np.log(df['otherpct']),0)
df['lum']=-(df['respct']*df['reslog']+
            df['offretpct']*df['offretlog']+
            df['otherpct']*df['otherlog'])/df['lumnum']
df.to_file(path+'ctlulum.shp')





df=gpd.read_file(path+'ctlulum.shp')
df.crs=4326
cttonta=pd.read_csv(path+'cttonta.csv',dtype=str)
df=pd.merge(df,cttonta,how='inner',on='tractid')
df['landlum']=df['land']*df['lum']
df=df.groupby(['ntacode'],as_index=False).agg({'landlum':'sum','land':'sum'}).reset_index(drop=True)
df['lum']=df['landlum']/df['land']
nta=gpd.read_file(path+'ntaclipped.shp')
nta.crs=4326
df=pd.merge(nta,df,how='inner',on='ntacode')
df=df.loc[~np.isin(df['ntacode'],['BK99','BX98','BX99','MN99','QN98','QN99','SI99']),['ntacode','ntaname','lum','geometry']].reset_index(drop=True)
df.to_file(path+'ntalulum.shp')















# dist=pd.DataFrame()
# dist['k']=range(1,10)
# dist['dist']=np.nan
# for k in range(1,10):
#     km=KMeans(n_clusters=k)
#     km=km.fit(df[['respct','offretpct','otherpct']])
#     dist.loc[dist['k']==k,'dist']=km.inertia_
# px.scatter(dist,'k','dist')




# k1=list(range(0,20))
# k2=[]
# for i in k1:
#     k2+=[len(k[k['btfar']>(k['ttfar']+i)])]
# px.scatter(x=k1,y=k2)



