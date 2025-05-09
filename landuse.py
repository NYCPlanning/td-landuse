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
from geosupport import Geosupport



pd.set_option('display.max_columns', None)
path='C:/Users/mayij/Desktop/DOC/DCP2021/LAND USE DIVERSITY/'
pio.renderers.default='browser'



# Get NYC block points
quadstatebkpt=gpd.read_file('C:/Users/mayij/Desktop/DOC/DCP2018/TRAVELSHEDREVAMP/shp/quadstatebkpt20.shp')
quadstatebkpt.crs=4326
quadstatebkpt['county']=[str(x)[0:5] for x in quadstatebkpt['blockid20']]
nycbkpt=quadstatebkpt.loc[quadstatebkpt['county'].isin(['36005','36047','36061','36081','36085']),['blockid20','geometry']].reset_index(drop=True)
nycbkpt.to_file(path+'nycbkpt20.shp')

# Get NYC block clipped
quadstatebk=gpd.read_file('C:/Users/mayij/Desktop/DOC/DCP2018/TRAVELSHEDREVAMP/shp/quadstatebkclipped20.shp')
quadstatebk.crs=4326
quadstatebk['county']=[str(x)[0:5] for x in quadstatebk['blockid20']]
nycbk=quadstatebk.loc[quadstatebk['county'].isin(['36005','36047','36061','36081','36085']),['blockid20','geometry']].reset_index(drop=True)
nycbk.to_file(path+'nycbkclipped20.shp')

# Get NYC tract clipped
quadstatect=gpd.read_file('C:/Users/mayij/Desktop/DOC/DCP2018/TRAVELSHEDREVAMP/shp/quadstatectclipped20.shp')
quadstatect.crs=4326
quadstatect['county']=[str(x)[0:5] for x in quadstatect['tractid20']]
nycct=quadstatect.loc[quadstatect['county'].isin(['36005','36047','36061','36081','36085']),['tractid20','geometry']].reset_index(drop=True)
nycct.to_file(path+'nycctclipped20.shp')

# Get OTP Walksheds
otpbkwk=gpd.read_file(path+'nycbkpt20.shp')
otpbkwk.crs=4326
otpbkwk['halfmile']=''
doserver='http://159.65.64.166:8801/'
for i in otpbkwk.index:
    try:
        url=doserver+'otp/routers/default/isochrone?batch=true&mode=WALK'
        url+='&fromPlace='+str(otpbkwk.loc[i,'geometry'].y)+','+str(otpbkwk.loc[i,'geometry'].x)
        url+='&cutoffSec=600'
        headers={'Accept':'application/json'}
        req=requests.get(url=url,headers=headers)
        js=req.json()
        iso=gpd.GeoDataFrame.from_features(js,crs=4326)
        otpbkwk.loc[i,'halfmile']=iso.loc[0,'geometry'].wkt
    except:
        otpbkwk.loc[i,'halfmile']=''
        print(str(otpbkwk.loc[i,'blockid20'])+' no geometry!')
otpbkwk=otpbkwk.loc[otpbkwk['halfmile']!='',['blockid20','halfmile']].reset_index(drop=True)
otpbkwk=gpd.GeoDataFrame(otpbkwk,geometry=otpbkwk['halfmile'].map(wkt.loads),crs=4326)
otpbkwk=otpbkwk.drop('halfmile',axis=1)
otpbkwk.to_file(path+'otpbkwk20.shp')





# Clean up MapPLUTO
# Block
df=gpd.read_file(path+'mappluto21.shp')
df.crs=4326
df['county']=df['Borough'].map({'BX':'36005','BK':'36047','MN':'36061','QN':'36081','SI':'36085'})
# df['tract']=pd.to_numeric(df['CT2010'])
# df=df[pd.notna(df['tract'])].reset_index(drop=True)
# df['tract']=[str(int(x*100)).zfill(6) for x in df['tract']]
# df['block']=pd.to_numeric(df['CB2010'])
# df=df[pd.notna(df['block'])].reset_index(drop=True)
# df['block']=[str(x).zfill(4) for x in df['block']]
# df['tractid']=df['county']+df['tract']
# df['blockid']=df['county']+df['tract']+df['block']
df['block']=[str(x)[1:] for x in df['BCTCB2020']]
df['blockid20']=df['county']+df['block']
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
df=df.groupby(['blockid20'],as_index=False).agg({'res':'sum','off':'sum','ret':'sum','grg':'sum',
                                                 'stg':'sum','fct':'sum','oth':'sum','bldg':'sum',
                                                 'shape':'sum'}).reset_index(drop=True)
pop=pd.read_csv(path+'pop2020.csv',dtype={'blockid20':str,'pop20':float})
df=pd.merge(df,pop,how='left',on='blockid20')
bk=gpd.read_file(path+'nycbkclipped20.shp')
bk.crs=4326
df=pd.merge(bk,df,how='inner',on='blockid20')
df.to_file(path+'bklu20.shp')

# # Tract
# df=gpd.read_file(path+'mappluto21.shp')
# df.crs=4326
# df['county']=df['Borough'].map({'BX':'36005','BK':'36047','MN':'36061','QN':'36081','SI':'36085'})
# # df['tract']=pd.to_numeric(df['CT2010'])
# # df=df[pd.notna(df['tract'])].reset_index(drop=True)
# # df['tract']=[str(int(x*100)).zfill(6) for x in df['tract']]
# # df['tractid']=df['county']+df['tract']
# df['tract']=[str(x)[1:] for x in df['BCT2020']]
# df['tractid20']=df['county']+df['tract']
# df['shape']=df['Shape_Area'].copy()
# df['bldg']=df['ResArea']+df['OfficeArea']+df['RetailArea']+df['GarageArea']+df['StrgeArea']+df['FactryArea']+df['OtherArea']
# df=df[df['bldg']!=0].reset_index(drop=True)
# df['ttfar']=df['ResidFAR']+df['CommFAR']+df['FacilFAR']
# df['btfar']=df['bldg']/df['shape']
# df=df[df['btfar']<=40].reset_index(drop=True)
# df['res']=df['ResArea'].copy()
# df['off']=df['OfficeArea'].copy()
# df['ret']=df['RetailArea'].copy()
# df['grg']=df['GarageArea'].copy()
# df['stg']=df['StrgeArea'].copy()
# df['fct']=df['FactryArea'].copy()
# df['oth']=df['OtherArea'].copy()
# df=df.groupby(['tractid20'],as_index=False).agg({'res':'sum','off':'sum','ret':'sum','grg':'sum',
#                                                  'stg':'sum','fct':'sum','oth':'sum','bldg':'sum',
#                                                  'shape':'sum'}).reset_index(drop=True)
# ct=gpd.read_file(path+'nycctclipped20.shp')
# ct.crs=4326
# df=pd.merge(ct,df,how='inner',on='tractid20')
# df.to_file(path+'ctlu20.shp')




# Half-Mile Walkshed
bk=gpd.read_file(path+'nycbkclipped20.shp')
bk.crs=4326
# bkwk=gpd.read_file(path+'nycbkhalfmile.shp')
# bkwk.crs=4326
# bkwk['blockid']=[x.split(':')[0].strip() for x in bkwk['Name']]
# bkwk=bkwk[['blockid','geometry']].reset_index(drop=True)
bkwk=gpd.read_file(path+'otpbkwk20.shp')
bkwk.crs=4326
df=gpd.sjoin(bkwk,bk,how='inner',op='intersects')
bklu=gpd.read_file(path+'bklu20.shp')
bklu.crs=4326
df=pd.merge(df,bklu,how='inner',left_on='blockid20_right',right_on='blockid20')
df=df.groupby(['blockid20_left'],as_index=False).agg({'res':'sum','off':'sum','ret':'sum','grg':'sum',
                                                      'stg':'sum','fct':'sum','oth':'sum','bldg':'sum',
                                                      'shape':'sum','pop20':'sum'}).reset_index(drop=True)
df.columns=['blockid20','res','off','ret','grg','stg','fct','oth','bldg','shape','pop20']
df=pd.merge(bk,df,how='inner',on='blockid20')
df.to_file(path+'bkwklu20.shp')





# Land use entropy
# Cat3
# Block
df=gpd.read_file(path+'bkwklu20.shp')
df.crs=4326
df['tractid20']=[str(x)[0:11] for x in df['blockid20']]
cttonta=pd.read_csv(path+'cttonta20.csv',dtype=str)
df=pd.merge(df,cttonta,how='inner',on='tractid20')
# df=df.loc[~np.isin(df['ntacode20'],['BK99','BX98','BX99','MN99','QN98','QN99','SI99'])].reset_index(drop=True)
# df=df.drop(['tractid20','ntacode','ntaname'],axis=1)
df=df[df['ntatype']=='0'].reset_index(drop=True)
df=df.drop(['tractid20','ntacode20','ntaname','ntatype'],axis=1)
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
df['cat']=np.where(df['ludi']<0.5,'0.00~0.49',
          np.where(df['ludi']<0.6,'0.50~0.59',
          np.where(df['ludi']<0.7,'0.60~0.69',
          np.where(df['ludi']<0.8,'0.70~0.79',
                   '0.80~1.00'))))
df.to_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-landuse/bkwkcat3ludi.geojson',driver='GeoJSON')


# Tract
df=gpd.read_file(path+'bkwkcat3ludi.shp')
df.crs=4326
df['tractid20']=[str(x)[0:11] for x in df['blockid20']]
df['bldgludi']=df['bldg']*df['ludi']
df=df.groupby(['tractid20'],as_index=False).agg({'bldgludi':'sum','bldg':'sum'}).reset_index(drop=True)
df['ludi']=df['bldgludi']/df['bldg']
ct=gpd.read_file(path+'nycctclipped20.shp')
ct.crs=4326
df=pd.merge(ct,df,how='inner',on='tractid20')
cttonta=pd.read_csv(path+'cttonta20.csv',dtype=str)
df=pd.merge(df,cttonta,how='inner',on='tractid20')
# df=df.loc[~np.isin(df['ntacode'],['BK99','BX98','BX99','MN99','QN98','QN99','SI99']),['tractid20','ludi','geometry']].reset_index(drop=True)
df=df[df['ntatype']=='0'].reset_index(drop=True)
df=df.drop(['ntacode20','ntaname','ntatype'],axis=1)
df.to_file(path+'ctcat3ludi.shp')
df['ludi'].describe(percentiles=np.arange(0.2,1,0.2))
df['cat']=np.where(df['ludi']<0.5,'0.00~0.49',
          np.where(df['ludi']<0.6,'0.50~0.59',
          np.where(df['ludi']<0.7,'0.60~0.69',
          np.where(df['ludi']<0.8,'0.70~0.79',
                   '0.80~1.00'))))
df.to_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-landuse/ctcat3ludi.geojson',driver='GeoJSON')


# NTA
df=gpd.read_file(path+'bkwkcat3ludi.shp')
df.crs=4326
df['tractid20']=[str(x)[0:11] for x in df['blockid20']]
cttonta=pd.read_csv(path+'cttonta20.csv',dtype=str)
df=pd.merge(df,cttonta,how='inner',on='tractid20')
df['bldgludi']=df['bldg']*df['ludi']
df=df.groupby(['ntacode20'],as_index=False).agg({'bldgludi':'sum','bldg':'sum'}).reset_index(drop=True)
df['ludi']=df['bldgludi']/df['bldg']
nta=gpd.read_file(path+'ntaclipped20.shp')
nta.crs=4326
df=pd.merge(nta,df,how='inner',on='ntacode20')
# df=df.loc[~np.isin(df['ntacode'],['BK99','BX98','BX99','MN99','QN98','QN99','SI99']),['ntacode','ntaname','ludi','geometry']].reset_index(drop=True)
df=df[df['ntatype']=='0'].reset_index(drop=True)
df.to_file(path+'ntacat3ludi.shp')
df['ludi'].describe(percentiles=np.arange(0.2,1,0.2))
df['cat']=np.where(df['ludi']<0.5,'0.00~0.49',
          np.where(df['ludi']<0.6,'0.50~0.59',
          np.where(df['ludi']<0.7,'0.60~0.69',
          np.where(df['ludi']<0.8,'0.70~0.79',
                   '0.80~1.00'))))
df.to_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-landuse/ntacat3ludi.geojson',driver='GeoJSON')







# Cat5
# Block
df=gpd.read_file(path+'bkwklu20.shp')
df.crs=4326
df['tractid20']=[str(x)[0:11] for x in df['blockid20']]
cttonta=pd.read_csv(path+'cttonta20.csv',dtype=str)
df=pd.merge(df,cttonta,how='inner',on='tractid20')
# df=df.loc[~np.isin(df['ntacode'],['BK99','BX98','BX99','MN99','QN98','QN99','SI99'])].reset_index(drop=True)
# df=df.drop(['tractid','ntacode'],axis=1)
df=df[df['ntatype']=='0'].reset_index(drop=True)
df=df.drop(['tractid20','ntacode20','ntaname','ntatype'],axis=1)
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
df['cat']=np.where(df['ludi']<0.4,'0.00~0.39',
          np.where(df['ludi']<0.5,'0.40~0.49',
          np.where(df['ludi']<0.6,'0.50~0.59',
          np.where(df['ludi']<0.7,'0.60~0.69',
                   '0.70~1.00'))))
df.to_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-landuse/bkwkcat5ludi.geojson',driver='GeoJSON')


# Tract
df=gpd.read_file(path+'bkwkcat5ludi.shp')
df.crs=4326
df['tractid20']=[str(x)[0:11] for x in df['blockid20']]
df['bldgludi']=df['bldg']*df['ludi']
df=df.groupby(['tractid20'],as_index=False).agg({'bldgludi':'sum','bldg':'sum'}).reset_index(drop=True)
df['ludi']=df['bldgludi']/df['bldg']
ct=gpd.read_file(path+'nycctclipped20.shp')
ct.crs=4326
df=pd.merge(ct,df,how='inner',on='tractid20')
cttonta=pd.read_csv(path+'cttonta20.csv',dtype=str)
df=pd.merge(df,cttonta,how='inner',on='tractid20')
# df=df.loc[~np.isin(df['ntacode'],['BK99','BX98','BX99','MN99','QN98','QN99','SI99']),['tractid','ludi','geometry']].reset_index(drop=True)
df=df[df['ntatype']=='0'].reset_index(drop=True)
df=df.drop(['ntacode20','ntaname','ntatype'],axis=1)
df.to_file(path+'ctcat5ludi.shp')
df['ludi'].describe(percentiles=np.arange(0.2,1,0.2))
df['cat']=np.where(df['ludi']<0.4,'0.00~0.39',
          np.where(df['ludi']<0.5,'0.40~0.49',
          np.where(df['ludi']<0.6,'0.50~0.59',
          np.where(df['ludi']<0.7,'0.60~0.69',
                   '0.70~1.00'))))
df.to_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-landuse/ctcat5ludi.geojson',driver='GeoJSON')


# NTA
df=gpd.read_file(path+'bkwkcat5ludi.shp')
df.crs=4326
df['tractid20']=[str(x)[0:11] for x in df['blockid20']]
cttonta=pd.read_csv(path+'cttonta20.csv',dtype=str)
df=pd.merge(df,cttonta,how='inner',on='tractid20')
df['bldgludi']=df['bldg']*df['ludi']
df=df.groupby(['ntacode20'],as_index=False).agg({'bldgludi':'sum','bldg':'sum'}).reset_index(drop=True)
df['ludi']=df['bldgludi']/df['bldg']
nta=gpd.read_file(path+'ntaclipped20.shp')
nta.crs=4326
df=pd.merge(nta,df,how='inner',on='ntacode20')
# df=df.loc[~np.isin(df['ntacode'],['BK99','BX98','BX99','MN99','QN98','QN99','SI99']),['ntacode','ntaname','ludi','geometry']].reset_index(drop=True)
df=df[df['ntatype']=='0'].reset_index(drop=True)
df.to_file(path+'ntacat5ludi.shp')
df['ludi'].describe(percentiles=np.arange(0.2,1,0.2))
df['cat']=np.where(df['ludi']<0.4,'0.00~0.39',
          np.where(df['ludi']<0.5,'0.40~0.49',
          np.where(df['ludi']<0.6,'0.50~0.59',
          np.where(df['ludi']<0.7,'0.60~0.69',
                   '0.70~1.00'))))
df.to_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-landuse/ntacat5ludi.geojson',driver='GeoJSON')





# Cat5 Adjusted
# Block
df=gpd.read_file(path+'bkwklu20.shp')
df.crs=4326
df['tractid20']=[str(x)[0:11] for x in df['blockid20']]
cttonta=pd.read_csv(path+'cttonta20.csv',dtype=str)
df=pd.merge(df,cttonta,how='inner',on='tractid20')
# df=df.loc[~np.isin(df['ntacode'],['BK99','BX98','BX99','MN99','QN98','QN99','SI99'])].reset_index(drop=True)
# df=df.drop(['tractid','ntacode'],axis=1)
df=df[df['ntatype']=='0'].reset_index(drop=True)
df=df.drop(['tractid20','ntacode20','ntaname','ntatype'],axis=1)
df['cat5res']=df['res']*1
df['cat5off']=df['off']*1.5
df['cat5ret']=df['ret']*10
df['cat5ind']=(df['grg']+df['stg']+df['fct'])*0.5
df['cat5other']=df['oth']*1
df['bldgadj']=df['cat5res']+df['cat5off']+df['cat5ret']+df['cat5ind']+df['cat5other']
df['respct']=df['cat5res']/df['bldgadj']
df['offpct']=df['cat5off']/df['bldgadj']
df['retpct']=df['cat5ret']/df['bldgadj']
df['indpct']=df['cat5ind']/df['bldgadj']
df['otherpct']=df['cat5other']/df['bldgadj']
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
df.to_file(path+'bkwkcat5adjludi.shp')
df['ludi'].describe(percentiles=np.arange(0.2,1,0.2))
df['cat']=np.where(df['ludi']<0.6,'0.00~0.59',
          np.where(df['ludi']<0.65,'0.60~0.64',
          np.where(df['ludi']<0.7,'0.65~0.69',
          np.where(df['ludi']<0.75,'0.70~0.74',
                   '0.75~1.00'))))
df.to_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-landuse/bkwkcat5adjludi.geojson',driver='GeoJSON')


# Tract
df=gpd.read_file(path+'bkwkcat5adjludi.shp')
df.crs=4326
df['tractid20']=[str(x)[0:11] for x in df['blockid20']]
df['bldgadjludi']=df['bldgadj']*df['ludi']
df=df.groupby(['tractid20'],as_index=False).agg({'bldgadjludi':'sum','bldgadj':'sum'}).reset_index(drop=True)
df['ludi']=df['bldgadjludi']/df['bldgadj']
ct=gpd.read_file(path+'nycctclipped20.shp')
ct.crs=4326
df=pd.merge(ct,df,how='inner',on='tractid20')
cttonta=pd.read_csv(path+'cttonta20.csv',dtype=str)
df=pd.merge(df,cttonta,how='inner',on='tractid20')
# df=df.loc[~np.isin(df['ntacode'],['BK99','BX98','BX99','MN99','QN98','QN99','SI99']),['tractid','ludi','geometry']].reset_index(drop=True)
df=df[df['ntatype']=='0'].reset_index(drop=True)
df=df.drop(['ntacode20','ntaname','ntatype'],axis=1)
df.to_file(path+'ctcat5adjludi.shp')
df['ludi'].describe(percentiles=np.arange(0.2,1,0.2))
df['cat']=np.where(df['ludi']<0.6,'0.00~0.59',
          np.where(df['ludi']<0.65,'0.60~0.64',
          np.where(df['ludi']<0.7,'0.65~0.69',
          np.where(df['ludi']<0.75,'0.70~0.74',
                   '0.75~1.00'))))
df.to_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-landuse/ctcat5adjludi.geojson',driver='GeoJSON')


# NTA
df=gpd.read_file(path+'bkwkcat5adjludi.shp')
df.crs=4326
df['tractid20']=[str(x)[0:11] for x in df['blockid20']]
cttonta=pd.read_csv(path+'cttonta20.csv',dtype=str)
df=pd.merge(df,cttonta,how='inner',on='tractid20')
df['bldgadjludi']=df['bldgadj']*df['ludi']
df=df.groupby(['ntacode20'],as_index=False).agg({'bldgadjludi':'sum','bldgadj':'sum'}).reset_index(drop=True)
df['ludi']=df['bldgadjludi']/df['bldgadj']
nta=gpd.read_file(path+'ntaclipped20.shp')
nta.crs=4326
df=pd.merge(nta,df,how='inner',on='ntacode20')
# df=df.loc[~np.isin(df['ntacode'],['BK99','BX98','BX99','MN99','QN98','QN99','SI99']),['ntacode','ntaname','ludi','geometry']].reset_index(drop=True)
df=df[df['ntatype']=='0'].reset_index(drop=True)
df.to_file(path+'ntacat5adjludi.shp')
df['ludi'].describe(percentiles=np.arange(0.2,1,0.2))
df['cat']=np.where(df['ludi']<0.6,'0.00~0.59',
          np.where(df['ludi']<0.65,'0.60~0.64',
          np.where(df['ludi']<0.7,'0.65~0.69',
          np.where(df['ludi']<0.75,'0.70~0.74',
                   '0.75~1.00'))))
df.to_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-landuse/ntacat5adjludi.geojson',driver='GeoJSON')





# Cat5 Adjusted 2
# Block
df=gpd.read_file(path+'bkwklu20.shp')
df.crs=4326
df['tractid20']=[str(x)[0:11] for x in df['blockid20']]
cttonta=pd.read_csv(path+'cttonta20.csv',dtype=str)
df=pd.merge(df,cttonta,how='inner',on='tractid20')
# df=df.loc[~np.isin(df['ntacode'],['BK99','BX98','BX99','MN99','QN98','QN99','SI99'])].reset_index(drop=True)
# df=df.drop(['tractid','ntacode'],axis=1)
df=df[df['ntatype']=='0'].reset_index(drop=True)
df=df.drop(['tractid20','ntacode20','ntaname','ntatype'],axis=1)
df['cat5res']=df['res']*1
df['cat5off']=df['off']*0.5
df['cat5ret']=df['ret']*10
df['cat5ind']=(df['grg']+df['stg']+df['fct'])*0.5
df['cat5other']=df['oth']*1
df['bldgadj']=df['cat5res']+df['cat5off']+df['cat5ret']+df['cat5ind']+df['cat5other']
df['respct']=df['cat5res']/df['bldgadj']
df['offpct']=df['cat5off']/df['bldgadj']
df['retpct']=df['cat5ret']/df['bldgadj']
df['indpct']=df['cat5ind']/df['bldgadj']
df['otherpct']=df['cat5other']/df['bldgadj']
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
df.to_file(path+'bkwkcat5adj2ludi.shp')
df['ludi'].describe(percentiles=np.arange(0.2,1,0.2))
df['cat']=np.where(df['ludi']<0.55,'0.00~0.54',
          np.where(df['ludi']<0.6,'0.55~0.59',
          np.where(df['ludi']<0.65,'0.60~0.64',
          np.where(df['ludi']<0.7,'0.65~0.69',
                   '0.70~1.00'))))
df.to_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-landuse/bkwkcat5adj2ludi.geojson',driver='GeoJSON')


# Tract
df=gpd.read_file(path+'bkwkcat5adj2ludi.shp')
df.crs=4326
df['tractid20']=[str(x)[0:11] for x in df['blockid20']]
df['bldgadjludi']=df['bldgadj']*df['ludi']
df=df.groupby(['tractid20'],as_index=False).agg({'bldgadjludi':'sum','bldgadj':'sum'}).reset_index(drop=True)
df['ludi']=df['bldgadjludi']/df['bldgadj']
ct=gpd.read_file(path+'nycctclipped20.shp')
ct.crs=4326
df=pd.merge(ct,df,how='inner',on='tractid20')
cttonta=pd.read_csv(path+'cttonta20.csv',dtype=str)
df=pd.merge(df,cttonta,how='inner',on='tractid20')
# df=df.loc[~np.isin(df['ntacode'],['BK99','BX98','BX99','MN99','QN98','QN99','SI99']),['tractid','ludi','geometry']].reset_index(drop=True)
df=df[df['ntatype']=='0'].reset_index(drop=True)
df=df.drop(['ntacode20','ntaname','ntatype'],axis=1)
df.to_file(path+'ctcat5adj2ludi.shp')
df['ludi'].describe(percentiles=np.arange(0.2,1,0.2))
df['cat']=np.where(df['ludi']<0.55,'0.00~0.54',
          np.where(df['ludi']<0.6,'0.55~0.59',
          np.where(df['ludi']<0.65,'0.60~0.64',
          np.where(df['ludi']<0.7,'0.65~0.69',
                   '0.70~1.00'))))
df.to_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-landuse/ctcat5adj2ludi.geojson',driver='GeoJSON')


# NTA
df=gpd.read_file(path+'bkwkcat5adj2ludi.shp')
df.crs=4326
df['tractid20']=[str(x)[0:11] for x in df['blockid20']]
cttonta=pd.read_csv(path+'cttonta20.csv',dtype=str)
df=pd.merge(df,cttonta,how='inner',on='tractid20')
df['bldgadjludi']=df['bldgadj']*df['ludi']
df=df.groupby(['ntacode20'],as_index=False).agg({'bldgadjludi':'sum','bldgadj':'sum'}).reset_index(drop=True)
df['ludi']=df['bldgadjludi']/df['bldgadj']
nta=gpd.read_file(path+'ntaclipped20.shp')
nta.crs=4326
df=pd.merge(nta,df,how='inner',on='ntacode20')
# df=df.loc[~np.isin(df['ntacode'],['BK99','BX98','BX99','MN99','QN98','QN99','SI99']),['ntacode','ntaname','ludi','geometry']].reset_index(drop=True)
df=df[df['ntatype']=='0'].reset_index(drop=True)
df.to_file(path+'ntacat5adj2ludi.shp')
df['ludi'].describe(percentiles=np.arange(0.2,1,0.2))
df['cat']=np.where(df['ludi']<0.55,'0.00~0.54',
          np.where(df['ludi']<0.6,'0.55~0.59',
          np.where(df['ludi']<0.65,'0.60~0.64',
          np.where(df['ludi']<0.7,'0.65~0.69',
                   '0.70~1.00'))))
df.to_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-landuse/ntacat5adj2ludi.geojson',driver='GeoJSON')








# Access to Retail
# Block
df=gpd.read_file(path+'bkwklu20.shp')
df.crs=4326
df['tractid20']=[str(x)[0:11] for x in df['blockid20']]
cttonta=pd.read_csv(path+'cttonta20.csv',dtype=str)
df=pd.merge(df,cttonta,how='inner',on='tractid20')
# df=df.loc[~np.isin(df['ntacode'],['BK99','BX98','BX99','MN99','QN98','QN99','SI99'])].reset_index(drop=True)
# df=df.drop(['tractid','ntacode'],axis=1)
df=df[df['ntatype']=='0'].reset_index(drop=True)
df=df.drop(['tractid20','ntacode20','ntaname','ntatype'],axis=1)
df['ludi']=np.where((df['ret']==0)|(df['res']==0),0,df['ret']/df['res'])
df.to_file(path+'bkwkcat2ludi.shp')
df0=df[df['ludi']==0].reset_index(drop=True)
df0['pct']=0
df=df[df['ludi']!=0].reset_index(drop=True)
df['pct']=pd.qcut(df['ludi'],100,labels=False)
df=pd.concat([df0,df],axis=0,ignore_index=True)
df['ludi'].describe(percentiles=np.arange(0.2,1,0.2))
df['cat']=np.where(df['ludi']<0.05,'0.00~0.04',
          np.where(df['ludi']<0.1,'0.05~0.09',
          np.where(df['ludi']<0.15,'0.10~0.14',
          np.where(df['ludi']<0.2,'0.15~0.19',
                   '>=0.20'))))
df['cat'].value_counts()
df.loc[(df['ludi']>0)&(df['ludi']<=0.3),'ludi'].hist(bins=100)
m=df.loc[(df['ludi']>0)&(df['ludi']<=0.15),'ludi'].mean()
s=df.loc[(df['ludi']>0)&(df['ludi']<=0.15),'ludi'].std()
df['score']=np.where(df['ludi']>=m+1.5*s,'Very High', 
            np.where(df['ludi']>=m+0.5*s,'High',
            np.where(df['ludi']>=m-0.5*s,'Medium',
            np.where(df['ludi']>=m-1.5*s,'Low','Very Low'))))
df['score'].hist()
df['score'].value_counts()
df.to_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-landuse/bkwkcat2ludi.geojson',driver='GeoJSON')


# Tract
df=gpd.read_file(path+'bkwkcat2ludi.shp')
df.crs=4326
df['tractid20']=[str(x)[0:11] for x in df['blockid20']]
df=df.groupby(['tractid20'],as_index=False).agg({'res':'sum','ret':'sum'}).reset_index(drop=True)
df['ludi']=np.where((df['ret']==0)|(df['res']==0),0,df['ret']/df['res'])
ct=gpd.read_file(path+'nycctclipped20.shp')
ct.crs=4326
df=pd.merge(ct,df,how='inner',on='tractid20')
cttonta=pd.read_csv(path+'cttonta20.csv',dtype=str)
df=pd.merge(df,cttonta,how='inner',on='tractid20')
# df=df.loc[~np.isin(df['ntacode'],['BK99','BX98','BX99','MN99','QN98','QN99','SI99']),['tractid','ludi','geometry']].reset_index(drop=True)
df=df[df['ntatype']=='0'].reset_index(drop=True)
df=df.drop(['ntacode20','ntaname','ntatype'],axis=1)
df.to_file(path+'ctcat2ludi.shp')
df0=df[df['ludi']==0].reset_index(drop=True)
df0['pct']=0
df=df[df['ludi']!=0].reset_index(drop=True)
df['pct']=pd.qcut(df['ludi'],100,labels=False)
df=pd.concat([df0,df],axis=0,ignore_index=True)
df['ludi'].describe(percentiles=np.arange(0.2,1,0.2))
df['cat']=np.where(df['ludi']<0.02,'0.00~0.01',
          np.where(df['ludi']<0.05,'0.02~0.04',
          np.where(df['ludi']<0.07,'0.05~0.06',
          np.where(df['ludi']<0.10,'0.07~0.09',
                   '>=0.10'))))
df['cat'].value_counts()
df.loc[(df['ludi']>0)&(df['ludi']<=0.2),'ludi'].hist(bins=100)
m=df.loc[(df['ludi']>0)&(df['ludi']<=0.15),'ludi'].mean()
s=df.loc[(df['ludi']>0)&(df['ludi']<=0.15),'ludi'].std()
df['score']=np.where(df['ludi']>=m+1.5*s,'Very High', 
            np.where(df['ludi']>=m+0.5*s,'High',
            np.where(df['ludi']>=m-0.5*s,'Medium',
            np.where(df['ludi']>=m-1.5*s,'Low','Very Low'))))
df['score'].hist()
df['score'].value_counts()
df.to_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-landuse/ctcat2ludi.geojson',driver='GeoJSON')


# NTA
df=gpd.read_file(path+'bkwkcat2ludi.shp')
df.crs=4326
df['tractid20']=[str(x)[0:11] for x in df['blockid20']]
cttonta=pd.read_csv(path+'cttonta20.csv',dtype=str)
df=pd.merge(df,cttonta,how='inner',on='tractid20')
df=df.groupby(['ntacode20'],as_index=False).agg({'res':'sum','ret':'sum'}).reset_index(drop=True)
df['ludi']=np.where((df['ret']==0)|(df['res']==0),0,df['ret']/df['res'])
nta=gpd.read_file(path+'ntaclipped20.shp')
nta.crs=4326
df=pd.merge(nta,df,how='inner',on='ntacode20')
# df=df.loc[~np.isin(df['ntacode'],['BK99','BX98','BX99','MN99','QN98','QN99','SI99']),['ntacode','ntaname','ludi','geometry']].reset_index(drop=True)
df=df[df['ntatype']=='0'].reset_index(drop=True)
df.to_file(path+'ntacat2ludi.shp')
df0=df[df['ludi']==0].reset_index(drop=True)
df0['pct']=0
df=df[df['ludi']!=0].reset_index(drop=True)
df['pct']=pd.qcut(df['ludi'],100,labels=False)
df=pd.concat([df0,df],axis=0,ignore_index=True)
df['ludi'].describe(percentiles=np.arange(0.2,1,0.2))
df['cat']=np.where(df['ludi']<0.05,'0.00~0.04',
          np.where(df['ludi']<0.1,'0.05~0.09',
          np.where(df['ludi']<0.15,'0.10~0.14',
          np.where(df['ludi']<0.2,'0.15~0.19',
                   '>=0.20'))))
df['cat'].value_counts()
df.loc[(df['ludi']>0)&(df['ludi']<=0.2),'ludi'].hist(bins=100)
m=df.loc[(df['ludi']>0)&(df['ludi']<=0.15),'ludi'].mean()
s=df.loc[(df['ludi']>0)&(df['ludi']<=0.15),'ludi'].std()
df['score']=np.where(df['ludi']>=m+1.5*s,'Very High', 
            np.where(df['ludi']>=m+0.5*s,'High',
            np.where(df['ludi']>=m-0.5*s,'Medium',
            np.where(df['ludi']>=m-1.5*s,'Low','Very Low'))))
df['score'].hist()
df['score'].value_counts()
df.to_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-landuse/ntacat2ludi.geojson',driver='GeoJSON')














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












# Access to Amenities
# ATM
atm=gpd.read_file(path+'amenities/BankOwnedATMLocations_191106/BankOwnedATMLocations_191106.shp')
atm.crs=6318
atm=atm.to_crs(4326)
atm=atm[atm['lat']!=0].reset_index(drop=True)
atm['atm']=1
atm=atm[['atm','geometry']].reset_index(drop=True)
# Day Care
daycare=gpd.read_file(path+'amenities/FacilitiesDayCare_191106/FacilitiesDayCare_191106.shp')
daycare.crs=4326
daycare['daycare']=1
daycare=daycare[['daycare','geometry']].reset_index(drop=True)
# Grocery Store
grocery=gpd.read_file(path+'amenities/GroceryStoresNYC_180802/GroceryStoresNYC_180802.shp')
grocery.crs=6539
grocery=grocery.to_crs(4326)
grocery['grocery']=1
grocery=grocery[['grocery','geometry']].reset_index(drop=True)
# Laundry
laundry=gpd.read_file(path+'amenities/LegallyOperatingBusinessesActiveSelfServiceLaundry_191106/LegallyOperatingBusinessesActiveSelfServiceLaundry_191106.shp')
laundry.crs=6539
laundry=laundry.to_crs(4326)
laundry['laundry']=1
laundry=laundry[['laundry','geometry']].reset_index(drop=True)
# Pharmacy
pharmacy=gpd.read_file(path+'amenities/PharmaciesMedicaidEnrolled_191106/PharmaciesMedicaidEnrolled_191106.shp')
pharmacy.crs=6318
pharmacy=pharmacy.to_crs(4326)
pharmacy=pharmacy.drop_duplicates(['SERVICE_AD','CITY','STATE'],keep='first').reset_index(drop=True)
pharmacy['pharmacy']=1
pharmacy=pharmacy[['pharmacy','geometry']].reset_index(drop=True)
# Combine all
df=pd.concat([atm,daycare,grocery,laundry,pharmacy],axis=0,ignore_index=True)
df=df.fillna(0)
# Join to Walkshed
bkwk=gpd.read_file(path+'otpbkwk20.shp')
bkwk.crs=4326
df=gpd.sjoin(bkwk,df,how='inner',op='intersects')
df=df.groupby(['blockid20'],as_index=False).agg({'atm':'sum','daycare':'sum','grocery':'sum','laundry':'sum',
                                                 'pharmacy':'sum'}).reset_index(drop=True)
bk=gpd.read_file(path+'nycbkclipped20.shp')
bk.crs=4326
df=pd.merge(bk,df,how='left',on='blockid20')
df=df.fillna(0)
df['amenities']=df['atm']+df['daycare']+df['grocery']+df['laundry']+df['pharmacy']
bkwklu=gpd.read_file(path+'bkwklu20.shp')
bkwklu.crs=4326
bkwklu=bkwklu[['blockid20','pop20']].reset_index(drop=True)
df=pd.merge(df,bkwklu,how='left',on='blockid20')
df=df.fillna(0)
df['ludi']=np.where((df['amenities']==0)|(df['pop20']==0),0,df['amenities']/df['pop20']*1000)
df['tractid20']=[str(x)[0:11] for x in df['blockid20']]
cttonta=pd.read_csv(path+'cttonta20.csv',dtype=str)
df=pd.merge(df,cttonta,how='inner',on='tractid20')
df=df[df['ntatype']=='0'].reset_index(drop=True)
df=df.drop(['tractid20','ntacode20','ntaname','ntatype'],axis=1)
df.to_file(path+'bkwkamenludi.shp')
df0=df[df['ludi']==0].reset_index(drop=True)
df0['pct']=0
df=df[df['ludi']!=0].reset_index(drop=True)
df['pct']=pd.qcut(df['ludi'],100,labels=False)
df=pd.concat([df0,df],axis=0,ignore_index=True)
df['ludi'].describe(percentiles=np.arange(0.2,1,0.2))
df['cat']=np.where(df['ludi']<=0.5,'0.0~0.5',
          np.where(df['ludi']<=1,'0.6~1.0',
          np.where(df['ludi']<=1.5,'1.1~1.5',
          np.where(df['ludi']<=2,'1.6~2.0',
                   '>2.0'))))
df['cat'].value_counts()
df.loc[(df['ludi']>0)&(df['ludi']<=3),'ludi'].hist(bins=100)
m=df.loc[(df['ludi']>0)&(df['ludi']<=2),'ludi'].mean()
s=df.loc[(df['ludi']>0)&(df['ludi']<=2),'ludi'].std()
df['score']=np.where(df['ludi']>=m+1.5*s,'Very High', 
            np.where(df['ludi']>=m+0.5*s,'High',
            np.where(df['ludi']>=m-0.5*s,'Medium',
            np.where(df['ludi']>=m-1.5*s,'Low','Very Low'))))
df['score'].hist()
df['score'].value_counts()
df.to_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-landuse/bkwkamenludi.geojson',driver='GeoJSON')


# Tract
df=gpd.read_file(path+'bkwkamenludi.shp')
df.crs=4326
df['tractid20']=[str(x)[0:11] for x in df['blockid20']]
df=df.groupby(['tractid20'],as_index=False).agg({'amenities':'sum','pop20':'sum'}).reset_index(drop=True)
df['ludi']=np.where((df['amenities']==0)|(df['pop20']==0),0,df['amenities']/df['pop20']*1000)
ct=gpd.read_file(path+'nycctclipped20.shp')
ct.crs=4326
df=pd.merge(ct,df,how='inner',on='tractid20')
cttonta=pd.read_csv(path+'cttonta20.csv',dtype=str)
df=pd.merge(df,cttonta,how='inner',on='tractid20')
df=df[df['ntatype']=='0'].reset_index(drop=True)
df=df.drop(['ntacode20','ntaname','ntatype'],axis=1)
df.to_file(path+'ctamenludi.shp')
df0=df[df['ludi']==0].reset_index(drop=True)
df0['pct']=0
df=df[df['ludi']!=0].reset_index(drop=True)
df['pct']=pd.qcut(df['ludi'],100,labels=False)
df=pd.concat([df0,df],axis=0,ignore_index=True)
df['ludi'].describe(percentiles=np.arange(0.2,1,0.2))
df['cat']=np.where(df['ludi']<=0.5,'0.0~0.5',
          np.where(df['ludi']<=1,'0.6~1.0',
          np.where(df['ludi']<=1.5,'1.1~1.5',
          np.where(df['ludi']<=2,'1.6~2.0',
                   '>2.0'))))
df['cat'].value_counts()
df.loc[(df['ludi']>0)&(df['ludi']<=3),'ludi'].hist(bins=100)
m=df.loc[(df['ludi']>0)&(df['ludi']<=2),'ludi'].mean()
s=df.loc[(df['ludi']>0)&(df['ludi']<=2),'ludi'].std()
df['score']=np.where(df['ludi']>=m+1.5*s,'Very High', 
            np.where(df['ludi']>=m+0.5*s,'High',
            np.where(df['ludi']>=m-0.5*s,'Medium',
            np.where(df['ludi']>=m-1.5*s,'Low','Very Low'))))
df['score'].hist()
df['score'].value_counts()
df.to_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-landuse/ctamenludi.geojson',driver='GeoJSON')


# NTA
df=gpd.read_file(path+'bkwkamenludi.shp')
df.crs=4326
df['tractid20']=[str(x)[0:11] for x in df['blockid20']]
cttonta=pd.read_csv(path+'cttonta20.csv',dtype=str)
df=pd.merge(df,cttonta,how='inner',on='tractid20')
df=df.groupby(['ntacode20'],as_index=False).agg({'amenities':'sum','pop20':'sum'}).reset_index(drop=True)
df['ludi']=np.where((df['amenities']==0)|(df['pop20']==0),0,df['amenities']/df['pop20']*1000)
nta=gpd.read_file(path+'ntaclipped20.shp')
nta.crs=4326
df=pd.merge(nta,df,how='inner',on='ntacode20')
df=df[df['ntatype']=='0'].reset_index(drop=True)
df.to_file(path+'ntaamenludi.shp')
df0=df[df['ludi']==0].reset_index(drop=True)
df0['pct']=0
df=df[df['ludi']!=0].reset_index(drop=True)
df['pct']=pd.qcut(df['ludi'],100,labels=False)
df=pd.concat([df0,df],axis=0,ignore_index=True)
df['ludi'].describe(percentiles=np.arange(0.2,1,0.2))
df['cat']=np.where(df['ludi']<=0.5,'0.0~0.5',
          np.where(df['ludi']<=1,'0.6~1.0',
          np.where(df['ludi']<=1.5,'1.1~1.5',
          np.where(df['ludi']<=2,'1.6~2.0',
                   '>2.0'))))
df['cat'].value_counts()
df.loc[(df['ludi']>0)&(df['ludi']<=3),'ludi'].hist(bins=100)
m=df.loc[(df['ludi']>0)&(df['ludi']<=2),'ludi'].mean()
s=df.loc[(df['ludi']>0)&(df['ludi']<=2),'ludi'].std()
df['score']=np.where(df['ludi']>=m+1.5*s,'Very High', 
            np.where(df['ludi']>=m+0.5*s,'High',
            np.where(df['ludi']>=m-0.5*s,'Medium',
            np.where(df['ludi']>=m-1.5*s,'Low','Very Low'))))
df['score'].hist()
df['score'].value_counts()
df.to_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-landuse/ntaamenludi.geojson',driver='GeoJSON')






# Transit Travelshed
# Transit Mobility
# Tract
df=gpd.read_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-travelshed/mapbox/tti.geojson')
df.crs=4326
cttonta=pd.read_csv(path+'cttonta.csv',dtype=str)
df=pd.merge(df,cttonta,how='inner',on='tractid')
df=df.loc[~np.isin(df['ntacode'],['BK99','BX98','BX99','MN99','QN98','QN99','SI99']),['tractid','mobindex','geometry']].reset_index(drop=True)
df.to_file(path+'ctmobludi.shp')
df['pct']=pd.qcut(df['mobindex'],100,labels=False)
df['mobindex'].describe(percentiles=np.arange(0.2,1,0.2))
df.loc[(df['mobindex']>0)&(df['mobindex']<=100000),'mobindex'].hist(bins=100)
m=df.loc[(df['mobindex']>0)&(df['mobindex']<=80000),'mobindex'].mean()
s=df.loc[(df['mobindex']>0)&(df['mobindex']<=80000),'mobindex'].std()
df['score']=np.where(df['mobindex']>=m+1.5*s,'Very High', 
            np.where(df['mobindex']>=m+0.5*s,'High',
            np.where(df['mobindex']>=m-0.5*s,'Medium',
            np.where(df['mobindex']>=m-1.5*s,'Low','Very Low'))))
df['score'].hist()
df['score'].value_counts()
df.to_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-landuse/ctmobludi.geojson',driver='GeoJSON')

# NTA
df=gpd.read_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-travelshed/mapbox/tti.geojson')
df.crs=4326
pop=pd.read_csv(path+'pop1519.csv',dtype={'tractid':str,'pop1519':float})
df=pd.merge(df,pop,how='left',on='tractid')
cttonta=pd.read_csv(path+'cttonta.csv',dtype=str)
df=pd.merge(df,cttonta,how='inner',on='tractid')
df['mobpop']=df['mobindex']*df['pop1519']
df=df.groupby(['ntacode'],as_index=False).agg({'mobpop':'sum','pop1519':'sum'}).reset_index(drop=True)
df['mobindex']=df['mobpop']/df['pop1519']
nta=gpd.read_file(path+'ntaclipped.shp')
nta.crs=4326
df=pd.merge(nta,df,how='inner',on='ntacode')
df=df.loc[~np.isin(df['ntacode'],['BK99','BX98','BX99','MN99','QN98','QN99','SI99']),['ntacode','ntaname','mobindex','geometry']].reset_index(drop=True)
df.to_file(path+'ntamobludi.shp')
df['pct']=pd.qcut(df['mobindex'],100,labels=False)
df['mobindex'].describe(percentiles=np.arange(0.2,1,0.2))
df.loc[(df['mobindex']>0)&(df['mobindex']<=100000),'mobindex'].hist(bins=100)
m=df.loc[(df['mobindex']>0)&(df['mobindex']<=80000),'mobindex'].mean()
s=df.loc[(df['mobindex']>0)&(df['mobindex']<=80000),'mobindex'].std()
df['score']=np.where(df['mobindex']>=m+1.5*s,'Very High', 
            np.where(df['mobindex']>=m+0.5*s,'High',
            np.where(df['mobindex']>=m-0.5*s,'Medium',
            np.where(df['mobindex']>=m-1.5*s,'Low','Very Low'))))
df['score'].hist()
df['score'].value_counts()
df.to_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-landuse/ntamobludi.geojson',driver='GeoJSON')



# Access to Population
# Tract
df=gpd.read_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-travelshed/mapbox/tti.geojson')
df.crs=4326
cttonta=pd.read_csv(path+'cttonta.csv',dtype=str)
df=pd.merge(df,cttonta,how='inner',on='tractid')
df=df.loc[~np.isin(df['ntacode'],['BK99','BX98','BX99','MN99','QN98','QN99','SI99']),['tractid','popindex','geometry']].reset_index(drop=True)
df.to_file(path+'ctpopludi.shp')
df['pct']=pd.qcut(df['popindex'],100,labels=False)
df['popindex'].describe(percentiles=np.arange(0.2,1,0.2))
df.loc[(df['popindex']>0)&(df['popindex']<=8000),'popindex'].hist(bins=100)
m=df.loc[(df['popindex']>0)&(df['popindex']<=6000),'popindex'].mean()
s=df.loc[(df['popindex']>0)&(df['popindex']<=6000),'popindex'].std()
df['score']=np.where(df['popindex']>=m+1.5*s,'Very High', 
            np.where(df['popindex']>=m+0.5*s,'High',
            np.where(df['popindex']>=m-0.5*s,'Medium',
            np.where(df['popindex']>=m-1.5*s,'Low','Very Low'))))
df['score'].hist()
df['score'].value_counts()
df.to_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-landuse/ctpopludi.geojson',driver='GeoJSON')

# NTA
df=gpd.read_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-travelshed/mapbox/tti.geojson')
df.crs=4326
pop=pd.read_csv(path+'pop1519.csv',dtype={'tractid':str,'pop1519':float})
df=pd.merge(df,pop,how='left',on='tractid')
cttonta=pd.read_csv(path+'cttonta.csv',dtype=str)
df=pd.merge(df,cttonta,how='inner',on='tractid')
df['poppop']=df['popindex']*df['pop1519']
df=df.groupby(['ntacode'],as_index=False).agg({'poppop':'sum','pop1519':'sum'}).reset_index(drop=True)
df['popindex']=df['poppop']/df['pop1519']
nta=gpd.read_file(path+'ntaclipped.shp')
nta.crs=4326
df=pd.merge(nta,df,how='inner',on='ntacode')
df=df.loc[~np.isin(df['ntacode'],['BK99','BX98','BX99','MN99','QN98','QN99','SI99']),['ntacode','ntaname','popindex','geometry']].reset_index(drop=True)
df.to_file(path+'ntapopludi.shp')
df['pct']=pd.qcut(df['popindex'],100,labels=False)
df['popindex'].describe(percentiles=np.arange(0.2,1,0.2))
df.loc[(df['popindex']>0)&(df['popindex']<=8000),'popindex'].hist(bins=100)
m=df.loc[(df['popindex']>0)&(df['popindex']<=6000),'popindex'].mean()
s=df.loc[(df['popindex']>0)&(df['popindex']<=6000),'popindex'].std()
df['score']=np.where(df['popindex']>=m+1.5*s,'Very High', 
            np.where(df['popindex']>=m+0.5*s,'High',
            np.where(df['popindex']>=m-0.5*s,'Medium',
            np.where(df['popindex']>=m-1.5*s,'Low','Very Low'))))
df['score'].hist()
df['score'].value_counts()
df.to_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-landuse/ntapopludi.geojson',driver='GeoJSON')



# Access to Jobs
# Tract
df=gpd.read_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-travelshed/mapbox/tti.geojson')
df.crs=4326
cttonta=pd.read_csv(path+'cttonta.csv',dtype=str)
df=pd.merge(df,cttonta,how='inner',on='tractid')
df=df.loc[~np.isin(df['ntacode'],['BK99','BX98','BX99','MN99','QN98','QN99','SI99']),['tractid','jobindex','geometry']].reset_index(drop=True)
df.to_file(path+'ctjobludi.shp')
df['pct']=pd.qcut(df['jobindex'],100,labels=False)
df['jobindex'].describe(percentiles=np.arange(0.2,1,0.2))
df.loc[(df['jobindex']>0)&(df['jobindex']<=3000),'jobindex'].hist(bins=100)
m=df.loc[(df['jobindex']>0)&(df['jobindex']<=2000),'jobindex'].mean()
s=df.loc[(df['jobindex']>0)&(df['jobindex']<=2000),'jobindex'].std()
df['score']=np.where(df['jobindex']>=m+1.5*s,'Very High', 
            np.where(df['jobindex']>=m+0.5*s,'High',
            np.where(df['jobindex']>=m-0.5*s,'Medium',
            np.where(df['jobindex']>=m-1.5*s,'Low','Very Low'))))
df['score'].hist()
df['score'].value_counts()
df.to_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-landuse/ctjobludi.geojson',driver='GeoJSON')

# NTA
df=gpd.read_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-travelshed/mapbox/tti.geojson')
df.crs=4326
pop=pd.read_csv(path+'pop1519.csv',dtype={'tractid':str,'pop1519':float})
df=pd.merge(df,pop,how='left',on='tractid')
cttonta=pd.read_csv(path+'cttonta.csv',dtype=str)
df=pd.merge(df,cttonta,how='inner',on='tractid')
df['jobpop']=df['jobindex']*df['pop1519']
df=df.groupby(['ntacode'],as_index=False).agg({'jobpop':'sum','pop1519':'sum'}).reset_index(drop=True)
df['jobindex']=df['jobpop']/df['pop1519']
nta=gpd.read_file(path+'ntaclipped.shp')
nta.crs=4326
df=pd.merge(nta,df,how='inner',on='ntacode')
df=df.loc[~np.isin(df['ntacode'],['BK99','BX98','BX99','MN99','QN98','QN99','SI99']),['ntacode','ntaname','jobindex','geometry']].reset_index(drop=True)
df.to_file(path+'ntapopludi.shp')
df['pct']=pd.qcut(df['jobindex'],100,labels=False)
df['jobindex'].describe(percentiles=np.arange(0.2,1,0.2))
df.loc[(df['jobindex']>0)&(df['jobindex']<=3000),'jobindex'].hist(bins=100)
m=df.loc[(df['jobindex']>0)&(df['jobindex']<=2000),'jobindex'].mean()
s=df.loc[(df['jobindex']>0)&(df['jobindex']<=2000),'jobindex'].std()
df['score']=np.where(df['jobindex']>=m+1.5*s,'Very High', 
            np.where(df['jobindex']>=m+0.5*s,'High',
            np.where(df['jobindex']>=m-0.5*s,'Medium',
            np.where(df['jobindex']>=m-1.5*s,'Low','Very Low'))))
df['score'].hist()
df['score'].value_counts()
df.to_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-landuse/ntajobludi.geojson',driver='GeoJSON')



# Access to Labor Force
# Tract
df=gpd.read_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-travelshed/mapbox/tti.geojson')
df.crs=4326
cttonta=pd.read_csv(path+'cttonta.csv',dtype=str)
df=pd.merge(df,cttonta,how='inner',on='tractid')
df=df.loc[~np.isin(df['ntacode'],['BK99','BX98','BX99','MN99','QN98','QN99','SI99']),['tractid','labindex','geometry']].reset_index(drop=True)
df.to_file(path+'ctlabludi.shp')
df['pct']=pd.qcut(df['labindex'],100,labels=False)
df['labindex'].describe(percentiles=np.arange(0.2,1,0.2))
df.loc[(df['labindex']>0)&(df['labindex']<=3000),'labindex'].hist(bins=100)
m=df.loc[(df['labindex']>0)&(df['labindex']<=2000),'labindex'].mean()
s=df.loc[(df['labindex']>0)&(df['labindex']<=2000),'labindex'].std()
df['score']=np.where(df['labindex']>=m+1.5*s,'Very High', 
            np.where(df['labindex']>=m+0.5*s,'High',
            np.where(df['labindex']>=m-0.5*s,'Medium',
            np.where(df['labindex']>=m-1.5*s,'Low','Very Low'))))
df['score'].hist()
df['score'].value_counts()
df.to_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-landuse/ctlabludi.geojson',driver='GeoJSON')

# NTA
df=gpd.read_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-travelshed/mapbox/tti.geojson')
df.crs=4326
pop=pd.read_csv(path+'pop1519.csv',dtype={'tractid':str,'pop1519':float})
df=pd.merge(df,pop,how='left',on='tractid')
cttonta=pd.read_csv(path+'cttonta.csv',dtype=str)
df=pd.merge(df,cttonta,how='inner',on='tractid')
df['labpop']=df['labindex']*df['pop1519']
df=df.groupby(['ntacode'],as_index=False).agg({'labpop':'sum','pop1519':'sum'}).reset_index(drop=True)
df['labindex']=df['labpop']/df['pop1519']
nta=gpd.read_file(path+'ntaclipped.shp')
nta.crs=4326
df=pd.merge(nta,df,how='inner',on='ntacode')
df=df.loc[~np.isin(df['ntacode'],['BK99','BX98','BX99','MN99','QN98','QN99','SI99']),['ntacode','ntaname','labindex','geometry']].reset_index(drop=True)
df.to_file(path+'ntapopludi.shp')
df['pct']=pd.qcut(df['labindex'],100,labels=False)
df['labindex'].describe(percentiles=np.arange(0.2,1,0.2))
df.loc[(df['labindex']>0)&(df['labindex']<=3000),'labindex'].hist(bins=100)
m=df.loc[(df['labindex']>0)&(df['labindex']<=2000),'labindex'].mean()
s=df.loc[(df['labindex']>0)&(df['labindex']<=2000),'labindex'].std()
df['score']=np.where(df['labindex']>=m+1.5*s,'Very High', 
            np.where(df['labindex']>=m+0.5*s,'High',
            np.where(df['labindex']>=m-0.5*s,'Medium',
            np.where(df['labindex']>=m-1.5*s,'Low','Very Low'))))
df['score'].hist()
df['score'].value_counts()
df.to_file('C:/Users/mayij/Desktop/DOC/GITHUB/td-landuse/ntalabludi.geojson',driver='GeoJSON')























# Access to Amenities with 2010 CT
# Tract
nycbkpt20=gpd.read_file(path+'nycbkpt20.shp')
nycbkpt20.crs=4326
quadstatect=gpd.read_file('C:/Users/mayij/Desktop/DOC/DCP2018/TRAVELSHEDREVAMP/shp/quadstatect.shp')
quadstatect.crs=4326
nycbkpt20=gpd.sjoin(nycbkpt20,quadstatect,how='inner',op='intersects')
nycbkpt20=nycbkpt20[['blockid20','tractid']].reset_index(drop=True)
df=gpd.read_file(path+'bkwkamenludi.shp')
df.crs=4326
df=pd.merge(df,nycbkpt20,how='inner',on='blockid20')
df=df.groupby(['tractid'],as_index=False).agg({'amenities':'sum','pop20':'sum'}).reset_index(drop=True)
df['ludi']=np.where((df['amenities']==0)|(df['pop20']==0),0,df['amenities']/df['pop20']*1000)
ct=gpd.read_file(path+'nycctclipped.shp')
ct.crs=4326
df=pd.merge(ct,df,how='inner',on='tractid')
cttonta=pd.read_csv(path+'cttonta.csv',dtype=str)
df=pd.merge(df,cttonta,how='inner',on='tractid')
df=df[~np.isin(df['ntacode'],['BK99','BX98','BX99','MN99','QN98','QN99','SI99'])].reset_index(drop=True)
df=df.drop(['ntacode'],axis=1)
df.to_file(path+'ctamenludi10.shp')
df0=df[df['ludi']==0].reset_index(drop=True)
df0['pct']=0
df=df[df['ludi']!=0].reset_index(drop=True)
df['pct']=pd.qcut(df['ludi'],100,labels=False)
df=pd.concat([df0,df],axis=0,ignore_index=True)
df['ludi'].describe(percentiles=np.arange(0.2,1,0.2))
df['cat']=np.where(df['ludi']<=0.5,'0.0~0.5',
          np.where(df['ludi']<=1,'0.6~1.0',
          np.where(df['ludi']<=1.5,'1.1~1.5',
          np.where(df['ludi']<=2,'1.6~2.0',
                   '>2.0'))))
df['cat'].value_counts()
df.loc[(df['ludi']>0)&(df['ludi']<=3),'ludi'].hist(bins=100)
m=df.loc[(df['ludi']>0)&(df['ludi']<=2),'ludi'].mean()
s=df.loc[(df['ludi']>0)&(df['ludi']<=2),'ludi'].std()
df['score']=np.where(df['ludi']>=m+1.5*s,'Very High', 
            np.where(df['ludi']>=m+0.5*s,'High',
            np.where(df['ludi']>=m-0.5*s,'Medium',
            np.where(df['ludi']>=m-1.5*s,'Low','Very Low'))))
df['score'].hist()
df['score'].value_counts()
df.to_file('C:/Users/mayij/Desktop/ctamenludi10.shp')

