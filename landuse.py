import geopandas as gpd
import numpy as np
import pandas as pd
import requests
import json
from shapely import wkt
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
from sklearn.cluster import KMeans



pd.set_option('display.max_columns', None)
path='C:/Users/mayij/Desktop/DOC/DCP2021/LAND USE DIVERSITY/'
pio.renderers.default='browser'



# Get NYC block points
quadstatebkpt=gpd.read_file('C:/Users/mayij/Desktop/DOC/DCP2018/TRAVELSHEDREVAMP/shp/quadstatebkpt.shp')
quadstatebkpt.crs=4326
quadstatebkpt['county']=[str(x)[0:5] for x in quadstatebkpt['blockid']]
nycbkpt=quadstatebkpt.loc[quadstatebkpt['county'].isin(['36005','36047','36061','36081','36085']),['blockid','geometry']].reset_index(drop=True)
nycbkpt.to_file(path+'nycbkpt.shp')

# Get NYC block clipped
quadstatebk=gpd.read_file('C:/Users/mayij/Desktop/DOC/DCP2018/TRAVELSHEDREVAMP/shp/quadstatebkclipped.shp')
quadstatebk.crs=4326
quadstatebk['county']=[str(x)[0:5] for x in quadstatebk['blockid']]
nycbk=quadstatebk.loc[quadstatebk['county'].isin(['36005','36047','36061','36081','36085']),['blockid','geometry']].reset_index(drop=True)
nycbk.to_file(path+'nycbkclipped.shp')

# Get OTP Walksheds
otpbkwk=gpd.read_file(path+'nycbkpt.shp')
otpbkwk.crs=4326
otpbkwk['halfmile']=''
doserver='http://159.65.64.166:8801/'
for i in otpbkwk.index:
    try:
        url=doserver+'otp/routers/default/isochrone?batch=true&mode=WALK'
        url+='&fromPlace='+str(quadstatebkpt.loc[i,'geometry'].y)+','+str(quadstatebkpt.loc[i,'geometry'].x)
        url+='&cutoffSec=600'
        headers={'Accept':'application/json'}
        req=requests.get(url=url,headers=headers)
        js=req.json()
        iso=gpd.GeoDataFrame.from_features(js,crs=4326)
        otpbkwk.loc[i,'halfmile']=iso.loc[0,'geometry'].wkt
    except:
        otpbkwk.loc[i,'halfmile']=''
        print(str(otpbkwk.loc[i,'blockid'])+' no geometry!')
otpbkwk=otpbkwk.loc[otpbkwk['halfmile']!='',['blockid','halfmile']].reset_index(drop=True)
otpbkwk=gpd.GeoDataFrame(otpbkwk,geometry=otpbkwk['halfmile'].map(wkt.loads),crs=4326)
otpbkwk=otpbkwk.drop('halfmile',axis=1)
otpbkwk.to_file(path+'otpbkwk.shp')





# Clean up MapPLUTO
# Tract
df=gpd.read_file(path+'mappluto.shp')
df.crs=4326
df['county']=df['Borough'].map({'BX':'36005','BK':'36047','MN':'36061','QN':'36081','SI':'36085'})
df['tract']=pd.to_numeric(df['CT2010'])
df=df[pd.notna(df['tract'])].reset_index(drop=True)
df['tract']=[str(int(x*100)).zfill(6) for x in df['tract']]
df['tractid']=df['county']+df['tract']
df['shape']=df['Shape_Area'].copy()
df['bldg']=df['ResArea']+df['OfficeArea']+df['RetailArea']+df['GarageArea']+df['StrgeArea']+df['FactryArea']+df['OtherArea']
df=df[df['bldg']!=0].reset_index(drop=True)
df['ttfar']=df['ResidFAR']+df['CommFAR']+df['FacilFAR']
df['btfar']=df['bldg']/df['shape']
df=df[df['btfar']<=40].reset_index(drop=True)
df['res']=df['ResArea'].copy()
df['off']=df['OfficeArea'].copy()
df['ret']=df['RetailArea'].copy()
df['grg']=df['GarageArea'].copy()
df['stg']=df['StrgeArea'].copy()
df['fct']=df['FactryArea'].copy()
df['oth']=df['OtherArea'].copy()
df=df.groupby(['tractid'],as_index=False).agg({'res':'sum','off':'sum','ret':'sum','grg':'sum',
                                               'stg':'sum','fct':'sum','oth':'sum','bldg':'sum',
                                               'shape':'sum'}).reset_index(drop=True)
ct=gpd.read_file(path+'nycctclipped.shp')
ct.crs=4326
df=pd.merge(ct,df,how='inner',on='tractid')
df.to_file(path+'ctlu.shp')



# Block
df=gpd.read_file(path+'mappluto.shp')
df.crs=4326
df['county']=df['Borough'].map({'BX':'36005','BK':'36047','MN':'36061','QN':'36081','SI':'36085'})
df['tract']=pd.to_numeric(df['CT2010'])
df=df[pd.notna(df['tract'])].reset_index(drop=True)
df['tract']=[str(int(x*100)).zfill(6) for x in df['tract']]
df['block']=pd.to_numeric(df['CB2010'])
df=df[pd.notna(df['block'])].reset_index(drop=True)
df['block']=[str(x).zfill(4) for x in df['block']]
df['tractid']=df['county']+df['tract']
df['blockid']=df['county']+df['tract']+df['block']
df['shape']=df['Shape_Area'].copy()
df['bldg']=df['ResArea']+df['OfficeArea']+df['RetailArea']+df['GarageArea']+df['StrgeArea']+df['FactryArea']+df['OtherArea']
df=df[df['bldg']!=0].reset_index(drop=True)
df['ttfar']=df['ResidFAR']+df['CommFAR']+df['FacilFAR']
df['btfar']=df['bldg']/df['shape']
df=df[df['btfar']<=40].reset_index(drop=True)
df['res']=df['ResArea'].copy()
df['off']=df['OfficeArea'].copy()
df['ret']=df['RetailArea'].copy()
df['grg']=df['GarageArea'].copy()
df['stg']=df['StrgeArea'].copy()
df['fct']=df['FactryArea'].copy()
df['oth']=df['OtherArea'].copy()
df=df.groupby(['blockid'],as_index=False).agg({'res':'sum','off':'sum','ret':'sum','grg':'sum',
                                               'stg':'sum','fct':'sum','oth':'sum','bldg':'sum',
                                               'shape':'sum'}).reset_index(drop=True)
bk=gpd.read_file(path+'nycbkclipped.shp')
bk.crs=4326
df=pd.merge(bk,df,how='inner',on='blockid')
df.to_file(path+'bklu.shp')



# Half-Mile Walkshed
bk=gpd.read_file(path+'nycbkclipped.shp')
bk.crs=4326
# bkwk=gpd.read_file(path+'nycbkhalfmile.shp')
# bkwk.crs=4326
# bkwk['blockid']=[x.split(':')[0].strip() for x in bkwk['Name']]
# bkwk=bkwk[['blockid','geometry']].reset_index(drop=True)
bkwk=gpd.read_file(path+'otpbkwk.shp')
bkwk.crs=4326
df=gpd.sjoin(bkwk,bk,how='inner',op='intersects')
bklu=gpd.read_file(path+'bklu.shp')
bklu.crs=4326
df=pd.merge(df,bklu,how='inner',left_on='blockid_right',right_on='blockid')
df=df.groupby(['blockid_left'],as_index=False).agg({'res':'sum','off':'sum','ret':'sum','grg':'sum',
                                                    'stg':'sum','fct':'sum','oth':'sum','bldg':'sum',
                                                    'shape':'sum'}).reset_index(drop=True)
df.columns=['blockid','res','off','ret','grg','stg','fct','oth','bldg','shape']
df=pd.merge(bk,df,how='inner',on='blockid')
df.to_file(path+'bkwklu.shp')





# Land use entropy
# Cat3
# Block
df=gpd.read_file(path+'bkwklu.shp')
df.crs=4326
df['tractid']=[str(x)[0:11] for x in df['blockid']]
cttonta=pd.read_csv(path+'cttonta.csv',dtype=str)
df=pd.merge(df,cttonta,how='inner',on='tractid')
df=df.loc[~np.isin(df['ntacode'],['BK99','BX98','BX99','MN99','QN98','QN99','SI99'])].reset_index(drop=True)
df=df.drop(['tractid','ntacode'],axis=1)
df['cat3res']=df['res'].copy()
df['cat3offret']=df['off']+df['ret']
df['cat3other']=df['grg']+df['stg']+df['fct']+df['oth']
df['respct']=df['cat3res']/df['bldg']
df['offretpct']=df['cat3offret']/df['bldg']
df['otherpct']=df['cat3other']/df['bldg']
df['reslog']=np.where(df['cat3res']>0,np.log(df['respct']),0)
df['offretlog']=np.where(df['cat3offret']>0,np.log(df['offretpct']),0)
df['otherlog']=np.where(df['cat3other']>0,np.log(df['otherpct']),0)
df['ludi']=-(df['respct']*df['reslog']+
            df['offretpct']*df['offretlog']+
            df['otherpct']*df['otherlog'])/np.log(3)
df.to_file(path+'bkwkcat3ludi.shp')
df['ludi'].describe(percentiles=np.arange(0.2,1,0.2))
df['cat']=np.where(df['ludi']<=0.5,'0.00~0.49',
          np.where(df['ludi']<=0.6,'0.50~0.59',
          np.where(df['ludi']<=0.7,'0.60~0.69',
          np.where(df['ludi']<=0.8,'0.70~0.79',
          '0.80~1.00'))))
df.to_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-landuse/bkwkcat3ludi.geojson',driver='GeoJSON')



# Tract
df=gpd.read_file(path+'bkwkcat3ludi.shp')
df.crs=4326
df['tractid']=[str(x)[0:11] for x in df['blockid']]
df['bldgludi']=df['bldg']*df['ludi']
df=df.groupby(['tractid'],as_index=False).agg({'bldgludi':'sum','bldg':'sum'}).reset_index(drop=True)
df['ludi']=df['bldgludi']/df['bldg']
ct=gpd.read_file(path+'nycctclipped.shp')
ct.crs=4326
df=pd.merge(ct,df,how='inner',on='tractid')
cttonta=pd.read_csv(path+'cttonta.csv',dtype=str)
df=pd.merge(df,cttonta,how='inner',on='tractid')
df=df.loc[~np.isin(df['ntacode'],['BK99','BX98','BX99','MN99','QN98','QN99','SI99']),['tractid','bldg','ludi','geometry']].reset_index(drop=True)
df.to_file(path+'ctcat3ludi.shp')
df['ludi'].describe(percentiles=np.arange(0.2,1,0.2))
df['cat']=np.where(df['ludi']<=0.5,'0.00~0.49',
          np.where(df['ludi']<=0.6,'0.50~0.59',
          np.where(df['ludi']<=0.7,'0.60~0.69',
          np.where(df['ludi']<=0.8,'0.70~0.79',
          '0.80~1.00'))))
df.to_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-landuse/ctcat3ludi.geojson',driver='GeoJSON')



# NTA
df=gpd.read_file(path+'bkwkcat3ludi.shp')
df.crs=4326
df['tractid']=[str(x)[0:11] for x in df['blockid']]
cttonta=pd.read_csv(path+'cttonta.csv',dtype=str)
df=pd.merge(df,cttonta,how='inner',on='tractid')
df['bldgludi']=df['bldg']*df['ludi']
df=df.groupby(['ntacode'],as_index=False).agg({'bldgludi':'sum','bldg':'sum'}).reset_index(drop=True)
df['ludi']=df['bldgludi']/df['bldg']
nta=gpd.read_file(path+'ntaclipped.shp')
nta.crs=4326
df=pd.merge(nta,df,how='inner',on='ntacode')
df=df.loc[~np.isin(df['ntacode'],['BK99','BX98','BX99','MN99','QN98','QN99','SI99']),['ntacode','ntaname','ludi','geometry']].reset_index(drop=True)
df.to_file(path+'ntacat3ludi.shp')
df['ludi'].describe(percentiles=np.arange(0.2,1,0.2))
df['cat']=np.where(df['ludi']<=0.5,'0.00~0.49',
          np.where(df['ludi']<=0.6,'0.50~0.59',
          np.where(df['ludi']<=0.7,'0.60~0.69',
          np.where(df['ludi']<=0.8,'0.70~0.79',
          '0.80~1.00'))))
df.to_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-landuse/ntacat3ludi.geojson',driver='GeoJSON')







# Cat5
# Block
df=gpd.read_file(path+'bkwklu.shp')
df.crs=4326
df['tractid']=[str(x)[0:11] for x in df['blockid']]
cttonta=pd.read_csv(path+'cttonta.csv',dtype=str)
df=pd.merge(df,cttonta,how='inner',on='tractid')
df=df.loc[~np.isin(df['ntacode'],['BK99','BX98','BX99','MN99','QN98','QN99','SI99'])].reset_index(drop=True)
df=df.drop(['tractid','ntacode'],axis=1)
df['cat5res']=df['res'].copy()
df['cat5off']=df['off'].copy()
df['cat5ret']=df['ret'].copy()
df['cat5ind']=df['grg']+df['stg']+df['fct']
df['cat5other']=df['oth'].copy()
df['respct']=df['cat5res']/df['bldg']
df['offpct']=df['cat5off']/df['bldg']
df['retpct']=df['cat5ret']/df['bldg']
df['indpct']=df['cat5ind']/df['bldg']
df['otherpct']=df['cat5other']/df['bldg']
df['reslog']=np.where(df['cat5res']>0,np.log(df['respct']),0)
df['offlog']=np.where(df['cat5off']>0,np.log(df['offpct']),0)
df['retlog']=np.where(df['cat5ret']>0,np.log(df['retpct']),0)
df['indlog']=np.where(df['cat5ind']>0,np.log(df['indpct']),0)
df['otherlog']=np.where(df['cat5other']>0,np.log(df['otherpct']),0)
df['ludi']=-(df['respct']*df['reslog']+
            df['offpct']*df['offlog']+
            df['retpct']*df['retlog']+
            df['indpct']*df['indlog']+
            df['otherpct']*df['otherlog'])/np.log(5)
df.to_file(path+'bkwkcat5ludi.shp')
df['ludi'].describe(percentiles=np.arange(0.2,1,0.2))
df['cat']=np.where(df['ludi']<=0.4,'0.00~0.39',
          np.where(df['ludi']<=0.5,'0.40~0.49',
          np.where(df['ludi']<=0.6,'0.50~0.59',
          np.where(df['ludi']<=0.7,'0.60~0.69',
          '0.70~1.00'))))
df.to_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-landuse/bkwkcat5ludi.geojson',driver='GeoJSON')



# Tract
df=gpd.read_file(path+'bkwkcat5ludi.shp')
df.crs=4326
df['tractid']=[str(x)[0:11] for x in df['blockid']]
df['bldgludi']=df['bldg']*df['ludi']
df=df.groupby(['tractid'],as_index=False).agg({'bldgludi':'sum','bldg':'sum'}).reset_index(drop=True)
df['ludi']=df['bldgludi']/df['bldg']
ct=gpd.read_file(path+'nycctclipped.shp')
ct.crs=4326
df=pd.merge(ct,df,how='inner',on='tractid')
cttonta=pd.read_csv(path+'cttonta.csv',dtype=str)
df=pd.merge(df,cttonta,how='inner',on='tractid')
df=df.loc[~np.isin(df['ntacode'],['BK99','BX98','BX99','MN99','QN98','QN99','SI99']),['tractid','bldg','ludi','geometry']].reset_index(drop=True)
df.to_file(path+'ctcat5ludi.shp')
df['ludi'].describe(percentiles=np.arange(0.2,1,0.2))
df['cat']=np.where(df['ludi']<=0.4,'0.00~0.39',
          np.where(df['ludi']<=0.5,'0.40~0.49',
          np.where(df['ludi']<=0.6,'0.50~0.59',
          np.where(df['ludi']<=0.7,'0.60~0.69',
          '0.70~1.00'))))
df.to_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-landuse/ctcat5ludi.geojson',driver='GeoJSON')



# NTA
df=gpd.read_file(path+'bkwkcat5ludi.shp')
df.crs=4326
df['tractid']=[str(x)[0:11] for x in df['blockid']]
cttonta=pd.read_csv(path+'cttonta.csv',dtype=str)
df=pd.merge(df,cttonta,how='inner',on='tractid')
df['bldgludi']=df['bldg']*df['ludi']
df=df.groupby(['ntacode'],as_index=False).agg({'bldgludi':'sum','bldg':'sum'}).reset_index(drop=True)
df['ludi']=df['bldgludi']/df['bldg']
nta=gpd.read_file(path+'ntaclipped.shp')
nta.crs=4326
df=pd.merge(nta,df,how='inner',on='ntacode')
df=df.loc[~np.isin(df['ntacode'],['BK99','BX98','BX99','MN99','QN98','QN99','SI99']),['ntacode','ntaname','ludi','geometry']].reset_index(drop=True)
df.to_file(path+'ntacat5ludi.shp')
df['ludi'].describe(percentiles=np.arange(0.2,1,0.2))
df['cat']=np.where(df['ludi']<=0.4,'0.00~0.39',
          np.where(df['ludi']<=0.5,'0.40~0.49',
          np.where(df['ludi']<=0.6,'0.50~0.59',
          np.where(df['ludi']<=0.7,'0.60~0.69',
          '0.70~1.00'))))
df.to_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-landuse/ntacat5ludi.geojson',driver='GeoJSON')





# Cat5 Weighted
# Block
df=gpd.read_file(path+'bkwklu.shp')
df.crs=4326
df['tractid']=[str(x)[0:11] for x in df['blockid']]
cttonta=pd.read_csv(path+'cttonta.csv',dtype=str)
df=pd.merge(df,cttonta,how='inner',on='tractid')
df=df.loc[~np.isin(df['ntacode'],['BK99','BX98','BX99','MN99','QN98','QN99','SI99'])].reset_index(drop=True)
df=df.drop(['tractid','ntacode'],axis=1)
df['cat5res']=df['res'].copy()
df['cat5off']=df['off'].copy()
df['cat5ret']=df['ret'].copy()
df['cat5ind']=df['grg']+df['stg']+df['fct']
df['cat5other']=df['oth'].copy()
df['respct']=df['cat5res']/df['bldg']
df['offpct']=df['cat5off']/df['bldg']
df['retpct']=df['cat5ret']/df['bldg']
df['indpct']=df['cat5ind']/df['bldg']
df['otherpct']=df['cat5other']/df['bldg']
df['reslog']=np.where(df['cat5res']>0,np.log(df['respct']),0)
df['offlog']=np.where(df['cat5off']>0,np.log(df['offpct']),0)
df['retlog']=np.where(df['cat5ret']>0,np.log(df['retpct']),0)
df['indlog']=np.where(df['cat5ind']>0,np.log(df['indpct']),0)
df['otherlog']=np.where(df['cat5other']>0,np.log(df['otherpct']),0)
df['ludi']=-(df['respct']*df['reslog']*1+
            df['offpct']*df['offlog']*1+
            df['retpct']*df['retlog']*5+
            df['indpct']*df['indlog']*0.25+
            df['otherpct']*df['otherlog']*1)/np.log(1+1+5+0.25+1)
df.to_file(path+'bkwkcat5wgtludi.shp')
df['ludi'].describe(percentiles=np.arange(0.2,1,0.2))
df['cat']=np.where(df['ludi']<=0.5,'0.00~0.49',
          np.where(df['ludi']<=0.6,'0.50~0.59',
          np.where(df['ludi']<=0.7,'0.60~0.69',
          np.where(df['ludi']<=0.8,'0.70~0.79',
          '0.80~1.00'))))
df.to_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-landuse/bkwkcat5wgtludi.geojson',driver='GeoJSON')



# Tract
df=gpd.read_file(path+'bkwkcat5wgtludi.shp')
df.crs=4326
df['tractid']=[str(x)[0:11] for x in df['blockid']]
df['bldgludi']=df['bldg']*df['ludi']
df=df.groupby(['tractid'],as_index=False).agg({'bldgludi':'sum','bldg':'sum'}).reset_index(drop=True)
df['ludi']=df['bldgludi']/df['bldg']
ct=gpd.read_file(path+'nycctclipped.shp')
ct.crs=4326
df=pd.merge(ct,df,how='inner',on='tractid')
cttonta=pd.read_csv(path+'cttonta.csv',dtype=str)
df=pd.merge(df,cttonta,how='inner',on='tractid')
df=df.loc[~np.isin(df['ntacode'],['BK99','BX98','BX99','MN99','QN98','QN99','SI99']),['tractid','bldg','ludi','geometry']].reset_index(drop=True)
df.to_file(path+'ctcat5wgtludi.shp')
df['ludi'].describe(percentiles=np.arange(0.2,1,0.2))
df['cat']=np.where(df['ludi']<=0.5,'0.00~0.49',
          np.where(df['ludi']<=0.6,'0.50~0.59',
          np.where(df['ludi']<=0.7,'0.60~0.69',
          np.where(df['ludi']<=0.8,'0.70~0.79',
          '0.80~1.00'))))
df.to_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-landuse/ctcat5wgtludi.geojson',driver='GeoJSON')



# NTA
df=gpd.read_file(path+'bkwkcat5wgtludi.shp')
df.crs=4326
df['tractid']=[str(x)[0:11] for x in df['blockid']]
cttonta=pd.read_csv(path+'cttonta.csv',dtype=str)
df=pd.merge(df,cttonta,how='inner',on='tractid')
df['bldgludi']=df['bldg']*df['ludi']
df=df.groupby(['ntacode'],as_index=False).agg({'bldgludi':'sum','bldg':'sum'}).reset_index(drop=True)
df['ludi']=df['bldgludi']/df['bldg']
nta=gpd.read_file(path+'ntaclipped.shp')
nta.crs=4326
df=pd.merge(nta,df,how='inner',on='ntacode')
df=df.loc[~np.isin(df['ntacode'],['BK99','BX98','BX99','MN99','QN98','QN99','SI99']),['ntacode','ntaname','ludi','geometry']].reset_index(drop=True)
df.to_file(path+'ntacat5wgtludi.shp')
df['ludi'].describe(percentiles=np.arange(0.2,1,0.2))
df['cat']=np.where(df['ludi']<=0.5,'0.00~0.49',
          np.where(df['ludi']<=0.6,'0.50~0.59',
          np.where(df['ludi']<=0.7,'0.60~0.69',
          np.where(df['ludi']<=0.8,'0.70~0.79',
          '0.80~1.00'))))
df.to_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-landuse/ntacat5wgtludi.geojson',driver='GeoJSON')

















# Clustering
# By FAR
df=gpd.read_file(path+'ctlu.shp')
df.crs=4326
df['resfar']=df['res']/df['land']
df['offretfar']=df['offret']/df['land']
df['otherfar']=df['other']/df['land']
dist=pd.DataFrame()
dist['k']=range(1,10)
dist['dist']=np.nan
for k in range(1,10):
    km=KMeans(n_clusters=k)
    km=km.fit(df[['resfar','offretfar','otherfar']])
    dist.loc[dist['k']==k,'dist']=km.inertia_
px.scatter(dist,'k','dist')
k=3 # Elbow
km=KMeans(n_clusters=k)
y=km.fit_predict(df[['resfar','offretfar','otherfar']])
df['farcluster']=y+1

# By Pct
df['respct']=df['res']/df['bldg']
df['offretpct']=df['offret']/df['bldg']
df['otherpct']=df['other']/df['bldg']
dist=pd.DataFrame()
dist['k']=range(1,10)
dist['dist']=np.nan
for k in range(1,10):
    km=KMeans(n_clusters=k)
    km=km.fit(df[['respct','offretpct','otherpct']])
    dist.loc[dist['k']==k,'dist']=km.inertia_
px.scatter(dist,'k','dist')
k=3 # Elbow
km=KMeans(n_clusters=k)
y=km.fit_predict(df[['respct','offretpct','otherpct']])
df['pctcluster']=y+1
df.to_file(path+'ctlucluster.shp')









# k=[]
# for i in range(0,100000):
#     a=np.random.uniform(0,1)
#     b=np.random.uniform(0,1-a)
#     c=1-a-b
#     lum=-(a*np.log(a)+b*np.log(b)+c*np.log(c))/np.log(3)
#     k+=[lum]
# px.histogram(k)

