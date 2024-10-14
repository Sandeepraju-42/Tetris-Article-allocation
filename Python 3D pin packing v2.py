# -*- coding: utf-8 -*-
"""
Created on Fri Sep 16 19:46:54 2022

@author: SandeepRaju
"""
###############################################################################
#Libraries
###############################################################################
import pandas as pd
import numpy as np

from py3dbp import Packer, Bin, Item #for 3D bin packing
#import binpacking as bp # a greedy binpacking problem solver package

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

import random
import gc
###############################################################################


###############################################################################
#reading data
###############################################################################
dir_path = 'C:/Users/sande/Desktop/Python learnings/Tetris/Tetris-Article-allocation/'
bin_rd = pd.read_excel(dir_path + 'RawData/Bin_sizes.xlsx')
cust_orders = pd.read_excel(dir_path + 'RawData/Customer_orders.xlsx')
buffer_percentage = 1.01
###############################################################################

###############################################################################
#Basic EDA
###############################################################################
print(bin_rd.head())
print(cust_orders.head())

#sort by customer and packages
cust_orders = cust_orders.sort_values(by=['Customer','Package'], ascending=True) 
print(cust_orders.Customer.unique())
print(cust_orders.Customer.count())
print(cust_orders.Customer.nunique())

cust_orders.groupby(['Customer']).agg(Min_g=('Weight/g',np.min), 
                                      max_g=('Weight/g',np.max),
                                      
                                      min_L=('Length/mm',np.min),
                                      max_L=('Length/mm',np.min),
                                      
                                      min_W=('Width/mm',np.min),
                                      max_W=('Width/mm',np.min),
                                      
                                      min_H=('Height/mm',np.min),
                                      max_H=('Height/mm',np.min)
                                      )

###############################################################################

###############################################################################
#UDFs
###############################################################################
#plot cubiod
def cuboid_data2(o, size=(1, 1, 1)):
    X = [[[0, 1, 0], [0, 0, 0], [1, 0, 0], [1, 1, 0]],
         [[0, 0, 0], [0, 0, 1], [1, 0, 1], [1, 0, 0]],
         [[1, 0, 1], [1, 0, 0], [1, 1, 0], [1, 1, 1]],
         [[0, 0, 1], [0, 0, 0], [0, 1, 0], [0, 1, 1]],
         [[0, 1, 0], [0, 1, 1], [1, 1, 1], [1, 1, 0]],
         [[0, 1, 1], [0, 0, 1], [1, 0, 1], [1, 1, 1]]]
    X = np.array(X).astype(float)
    for i in range(3):
        X[:, :, i] *= size[i]
    X += np.array(o)

    return X


def plotCubeAt2(positions, sizes=None, colors=None, **kwargs):
    if not isinstance(colors, (list, np.ndarray)): colors = ["C0"] * len(positions)
    if not isinstance(sizes, (list, np.ndarray)): sizes = [(1, 1, 1)] * len(positions)
    g = []
    for p, s, c in zip(positions, sizes, colors):
        g.append(cuboid_data2(p, size=s))
    return Poly3DCollection(np.concatenate(g),
                            facecolors=np.repeat(colors, 6), **kwargs)

#surface area of cardboard used
def cbsa(l,b,h):
    s1 = b*h
    s2 = l*h
    s3 = l*h
    s4 = b*h
    top = l*b
    bottom = l*b
    return(s1+s2+s3+s4+top+bottom)
###############################################################################  

    
###############################################################################  
#allocating into min boxes
###############################################################################  



###############################################################################
#Bin packing
###############################################################################


#Part 1
###############################################################################
#creating a simple cubiod that can fit all items

results_cube = pd.DataFrame(columns=['Customer', 
                                'Bin', 'Bin_Length', 'Bin_Width', 'Bin_Height', 'Bin_Max_weight','Bin_Volume',
                                'Fitted','Item', 'Item_Length', 'Item_Width', 'Item_Height', 'Item_Weight', 
                                'Pos_X', 'Pos_Y', 'Pos_Z', 'Rotation'])

for cust_name in cust_orders.Customer.unique(): 
    print(cust_name)
    
    #add packet details by customer
    cust_details = cust_orders[cust_orders.Customer == cust_name]
    cust_details['Volume'] = cust_details['Length/mm']*cust_details['Width/mm']*cust_details['Height/mm']
        
    #item count
    Item_Count = len(cust_details['Package'].unique())
    
    #divisior
    Item_Divisior = Item_Count/3
    
    # #cube root of total volume
    # cube_root = sum(cust_details['Volume']) ** (1. / 3)
    
    #generate bins with sum min side and sum max side of customer order
    max_l = int(round(sum(cust_details[['Length/mm','Width/mm','Height/mm']].max(axis=1))*buffer_percentage/Item_Divisior,0))
    min_l = int(round(sum(cust_details[['Length/mm','Width/mm','Height/mm']].min(axis=1))*buffer_percentage/Item_Divisior,0))
    count = 0
    fit_count = 0  
    
    #max weight is to be volume divided by an assumed factor of 2000, and rounded to 0
    for l in range(min_l,max_l,5):
        count = count + 1
        if fit_count >=len(cust_details.Package):
            break
         
        #setup packer object
        packer = Packer()
        
        #packer.add_item(Item('product name',length, width, height, weight))
        for index, row in cust_details.iterrows():
            #print(row['Package'], row['Length/mm'],row['Width/mm'],row['Height/mm'],row['Weight/g'])
            packer.add_item(Item(row['Package'], row['Length/mm'],row['Width/mm'],row['Height/mm'],row['Weight/g']))
        
        packer.add_bin(Bin('Bin_no_' + str(count), l, l, l, sum(cust_details['Weight/g'])+20)) #round(l*w*h/2000,0)
        
        packer.pack(bigger_first=True, distribute_items=True, number_of_decimals=0)
         # PACKING - by default (bigger_first=True,distribute_items=False,fix_point=True,number_of_decimals=0)

        for b in packer.bins:
            positions = []
            sizes = []
            colors = []
            lst = []
            

            #FITTED ITEMS
            for item in b.items:
                lst = [[cust_name, b.name, float(b.width), float(b.height), float(b.depth), float(b.max_weight), float(b.width * b.height * b.depth),
                       'Fitted', item.name, float(item.width), float(item.height), float(item.depth), float(item.weight),
                       float(item.position[0]), float(item.position[1]), float(item.position[2]), (item.rotation_type)
                       ]]
                fit_count = len(b.items)
                
                if fit_count >=len(cust_details.Package):
                                    
                    lst = pd.DataFrame(lst,columns=['Customer', 
                                                    'Bin', 'Bin_Length', 'Bin_Width', 'Bin_Height', 'Bin_Max_weight','Bin_Volume',
                                                    'Fitted','Item', 'Item_Length', 'Item_Width', 'Item_Height', 'Item_Weight', 
                                                    'Pos_X', 'Pos_Y', 'Pos_Z', 'Rotation'])
                    
                    results_cube = pd.concat([results_cube, lst], ignore_index=True, sort=False)
            del(packer)




#add details to results_cube
results_cube['Volume'] = results_cube['Item_Width']*results_cube['Item_Length']*results_cube['Item_Height']

results_cube_agg = pd.DataFrame(results_cube.groupby(['Customer'])['Volume'].agg('sum')).reset_index()
results_cube_agg.columns = ['Customer','Agg_Volume']


results_cube = pd.merge(results_cube,results_cube_agg, how='inner', on = 'Customer')
results_cube['FillRateRatio'] = results_cube['Agg_Volume']/results_cube['Bin_Volume']

#lower dimension
results_cube['Ratio_Dim'] = results_cube['FillRateRatio']*results_cube['Bin_Length']

#cleanup
del(l,lst,max_l,min_l,positions,results_cube_agg,row,sizes, item)
del(b, colors,count,cust_name, fit_count,index,Item_Count,Item_Divisior)



#Part 2
###############################################################################
#fine tuning the box dimensions from a cubiod

results = pd.DataFrame(columns=['Customer', 
                                'Bin', 'Bin_Length', 'Bin_Width', 'Bin_Height', 'Bin_Max_weight','Bin_Volume',
                                'Fitted','Item', 'Item_Length', 'Item_Width', 'Item_Height', 'Item_Weight', 
                                'Pos_X', 'Pos_Y', 'Pos_Z', 'Rotation'])

for cust_name in cust_orders.Customer.unique(): 
    print(cust_name)
   
    #add packet details by customer
    cust_details = results_cube[results_cube.Customer == cust_name]
        
    #item count
    Item_Count = len(cust_details['Item'].unique())
    
    #generate bins with sum min side and sum max side of customer order
    if cust_details['FillRateRatio'].max() < 0.65:
        min_l = int(round(min(cust_details['Ratio_Dim'])*3/4,0)) - 10
        max_l = int(max(cust_details['Bin_Length'])) + 10
    else:
        min_l = int(round(min(cust_details['Ratio_Dim']),0)) - 10
        max_l = int(max(cust_details['Bin_Length'])) + 10
    
    
    
    count = 0
    fit_count = 0  
    
    for l in range(min_l,max_l,1):
        for w in range(min_l,max_l,1):
            for h in range(min_l,max_l,1):
                count = count + 1
                if fit_count >= Item_Count:
                  break
       
         
        #setup packer object
        packer = Packer()
        
        #packer.add_item(Item('product name',length, width, height, weight))
        for index, row in cust_details.iterrows():
            packer.add_item(Item(row['Item'], row['Item_Length'],row['Item_Width'],row['Item_Height'],row['Item_Weight']))
        
        packer.add_bin(Bin('Bin_no_lwh_' + str(count), l, w, h, sum(cust_details['Item_Weight'])+200)) #round(l*w*h/2000,0)
        packer.add_bin(Bin('Bin_no_lhw_' + str(count), l, h, w, sum(cust_details['Item_Weight'])+200)) #round(l*w*h/2000,0)
        packer.add_bin(Bin('Bin_no_hwl_' + str(count), h, w, l, sum(cust_details['Item_Weight'])+200)) #round(l*w*h/2000,0)
        packer.add_bin(Bin('Bin_no_hlw_' + str(count), h, l, w, sum(cust_details['Item_Weight'])+200)) #round(l*w*h/2000,0)
        packer.add_bin(Bin('Bin_no_whl_' + str(count), w, h, l, sum(cust_details['Item_Weight'])+200)) #round(l*w*h/2000,0)
        packer.add_bin(Bin('Bin_no_wlh_' + str(count), w, l, h, sum(cust_details['Item_Weight'])+200)) #round(l*w*h/2000,0)



        packer.pack(bigger_first=True, distribute_items=False, number_of_decimals=0)
         # PACKING - by default (bigger_first=True,distribute_items=False,fix_point=True,number_of_decimals=0)

        for b in packer.bins:
            positions = []
            sizes = []
            colors = []
            lst = []
            

            #FITTED ITEMS
            for item in b.items:
                lst = [[cust_name, b.name, float(b.width), float(b.height), float(b.depth), float(b.max_weight), float(b.width * b.height * b.depth),
                       'Fitted', item.name, float(item.width), float(item.height), float(item.depth), float(item.weight),
                       float(item.position[0]), float(item.position[1]), float(item.position[2]), (item.rotation_type)
                       ]]
                fit_count = len(b.items)
                
                if fit_count == len(cust_details.Item):
                                    
                    lst = pd.DataFrame(lst,columns=['Customer', 
                                                    'Bin', 'Bin_Length', 'Bin_Width', 'Bin_Height', 'Bin_Max_weight','Bin_Volume',
                                                    'Fitted','Item', 'Item_Length', 'Item_Width', 'Item_Height', 'Item_Weight', 
                                                    'Pos_X', 'Pos_Y', 'Pos_Z', 'Rotation'])
                    
                    results = pd.concat([results, lst], ignore_index=True, sort=False)
                   
                    

        del(packer)
        gc.collect()

del(l,w,h,b,colors,count,fit_count, index, item, Item_Count, lst, max_l, min_l, positions, row, sizes)

#chosing the most optimal bin
#add details to results_cube
results['Volume'] = results['Item_Width']*results['Item_Length']*results['Item_Height']

results_agg = pd.DataFrame(results.groupby(['Customer','Bin'])['Volume'].agg('sum')).reset_index()
results_agg.columns = ['Customer','Bin','Agg_Volume']


results = pd.merge(results,results_agg, how='inner', on = ['Customer','Bin'])
results['FillRateRatio'] = results['Agg_Volume']/results['Bin_Volume']

#lower dimension
results['Ratio_Dim'] = results['FillRateRatio']*results['Bin_Length']

#append
results_Final = pd.concat([results,results_cube])

#sort based on lowest fillrate
results_Final = results_Final.sort_values(by=['Customer','Item','FillRateRatio'], ascending=False) 

#remove duplicates
results_Final = results_Final.drop_duplicates(subset=['Customer','Item'])

#stats
print(results_Final.FillRateRatio.mean())
print(results_Final.FillRateRatio.max())
print(results_Final.FillRateRatio.min())

#write results
results_Final.to_excel(dir_path + "Output/" + "results_Final.xlsx")


#Plot vars
for cust_name in results_Final.Customer.unique(): 
    print(cust_name)
    cust_details = results_Final[results_Final.Customer == cust_name].reset_index()
    cust_details = cust_details.sort_values(by=['Volume'], ascending=False).reset_index()
    positions=[]
    sizes=[]
    colors=[]
    
    for index, row in cust_details.iterrows():
        x = float(row['Pos_X']) #w
        y = float(row['Pos_Y']) #h
        z = float(row['Pos_Z']) #d
        positions.append((x, y, z))
        
        #rotations     RT_WHD = 0,    RT_HWD = 1,    RT_HDW = 2,    RT_DHW = 3,    RT_DWH = 4,    RT_WDH = 5
        w = float(row['Item_Length'])
        h = float(row['Item_Width'])
        d = float(row['Item_Height'])
        if row['Rotation'] == 0:sizes.append((w,h,d))
        if row['Rotation'] == 1:sizes.append((h,w,d))
        if row['Rotation'] == 2:sizes.append((h,d,w))
        if row['Rotation'] == 3:sizes.append((d,h,w))
        if row['Rotation'] == 4:sizes.append((d,w,h))
        if row['Rotation'] == 5:sizes.append((w,d,h))  
        
        r = lambda: random.randint(0,255)
        colors.append('#%02X%02X%02X' % (r(),r(),r()))

        #plot
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        #ax.set_aspect('auto')
        pc = plotCubeAt2(positions, sizes, colors=colors, edgecolor="k")
        ax.add_collection3d(pc)
        plt.title(cust_name + ' ' + row['Item'])
        ax.set_ylim([0, float(row['Bin_Length'])])
        ax.set_zlim([0, float(row['Bin_Width'])])
        ax.set_xlim([0, float(row['Bin_Height'])])
        plt.savefig(dir_path + "Plots/" + cust_name + str(index) + row['Item'] + '.png')