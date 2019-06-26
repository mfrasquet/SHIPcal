#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 17:36:28 2019

@author: miguel
"""

def arrays_Savings_Month(Q_prod_lim,Demand,fuel_cost,boiler_eff):
 #Para resumen mensual      

    Ene_sav_lim=np.zeros(8760)
    Feb_sav_lim=np.zeros(8760)
    Mar_sav_lim=np.zeros(8760)
    Abr_sav_lim=np.zeros(8760)
    May_sav_lim=np.zeros(8760)
    Jun_sav_lim=np.zeros(8760)
    Jul_sav_lim=np.zeros(8760)
    Ago_sav_lim=np.zeros(8760)
    Sep_sav_lim=np.zeros(8760)
    Oct_sav_lim=np.zeros(8760)
    Nov_sav_lim=np.zeros(8760)
    Dic_sav_lim=np.zeros(8760)
    Ene_demd=np.zeros(8760)
    Feb_demd=np.zeros(8760)
    Mar_demd=np.zeros(8760)
    Abr_demd=np.zeros(8760)
    May_demd=np.zeros(8760)
    Jun_demd=np.zeros(8760)
    Jul_demd=np.zeros(8760)
    Ago_demd=np.zeros(8760)
    Sep_demd=np.zeros(8760)
    Oct_demd=np.zeros(8760)
    Nov_demd=np.zeros(8760)
    Dic_demd=np.zeros(8760)
    Ene_frac=np.zeros(8760)
    Feb_frac=np.zeros(8760)
    Mar_frac=np.zeros(8760)
    Abr_frac=np.zeros(8760)
    May_frac=np.zeros(8760)
    Jun_frac=np.zeros(8760)
    Jul_frac=np.zeros(8760)
    Ago_frac=np.zeros(8760)
    Sep_frac=np.zeros(8760)
    Oct_frac=np.zeros(8760)
    Nov_frac=np.zeros(8760)
    Dic_frac=np.zeros(8760)

    for i in range(0,8759):
        if (i<=744-1):
            Ene_sav_lim[i]=fuel_cost*Q_prod_lim[i]/boiler_eff
            Ene_demd[i]=fuel_cost*Demand[i]
            Ene_frac[i]=Ene_sav_lim[i]/Ene_demd[i]
        if (i>744-1) and (i<=1416-1):
            Feb_sav_lim[i]=fuel_cost*Q_prod_lim[i]/boiler_eff
            Feb_demd[i]=fuel_cost*Demand[i]
            Feb_frac[i]=Feb_sav_lim[i]/Feb_demd[i]
        if (i>1416-1) and (i<=2160-1):
            Mar_sav_lim[i]=fuel_cost*Q_prod_lim[i]/boiler_eff
            Mar_demd[i]=fuel_cost*Demand[i]
            Mar_frac[i]=Mar_sav_lim[i]/Mar_demd[i]
        if (i>2160-1) and (i<=2880-1):
            Abr_sav_lim[i]=fuel_cost*Q_prod_lim[i]/boiler_eff
            Abr_demd[i]=fuel_cost*Demand[i]
            Abr_frac[i]=Abr_sav_lim[i]/Abr_demd[i]
        if (i>2880-1) and (i<=3624-1):
            May_sav_lim[i]=fuel_cost*Q_prod_lim[i]/boiler_eff
            May_demd[i]=fuel_cost*Demand[i]
            May_frac[i]=May_sav_lim[i]/May_demd[i]
        if (i>3624-1) and (i<=4344-1):
            Jun_sav_lim[i]=fuel_cost*Q_prod_lim[i]/boiler_eff
            Jun_demd[i]=fuel_cost*Demand[i]
            Jun_frac[i]=Jun_sav_lim[i]/Jun_demd[i]
        if (i>4344-1) and (i<=5088-1):
            Jul_sav_lim[i]=fuel_cost*Q_prod_lim[i]/boiler_eff
            Jul_demd[i]=fuel_cost*Demand[i]
            Jul_frac[i]=Jul_sav_lim[i]/Jul_demd[i]
        if (i>5088-1) and (i<=5832-1):
            Ago_sav_lim[i]=fuel_cost*Q_prod_lim[i]/boiler_eff
            Ago_demd[i]=fuel_cost*Demand[i]
            Ago_frac[i]=Ago_sav_lim[i]/Ago_demd[i]
        if (i>5832-1) and (i<=6552-1):
            Sep_sav_lim[i]=fuel_cost*Q_prod_lim[i]/boiler_eff
            Sep_demd[i]=fuel_cost*Demand[i]
            Sep_frac[i]=Sep_sav_lim[i]/Sep_demd[i]
        if (i>6552-1) and (i<=7296-1):
            Oct_sav_lim[i]=fuel_cost*Q_prod_lim[i]/boiler_eff
            Oct_demd[i]=fuel_cost*Demand[i]
            Oct_frac[i]=Oct_sav_lim[i]/Oct_demd[i]
        if (i>7296-1) and (i<=8016-1):
            Nov_sav_lim[i]=fuel_cost*Q_prod_lim[i]/boiler_eff
            Nov_demd[i]=fuel_cost*Demand[i]
            Nov_frac[i]=Nov_sav_lim[i]/Nov_demd[i]
        if (i>8016-1):
            Dic_sav_lim[i]=fuel_cost*Q_prod_lim[i]/boiler_eff
            Dic_demd[i]=fuel_cost*Demand[i]
            Dic_frac[i]=Dic_sav_lim[i]/Dic_demd[i]
    array_de_meses_lim=[np.sum(Ene_sav_lim),np.sum(Feb_sav_lim),np.sum(Mar_sav_lim),np.sum(Abr_sav_lim),np.sum(May_sav_lim),np.sum(Jun_sav_lim),np.sum(Jul_sav_lim),np.sum(Ago_sav_lim),np.sum(Sep_sav_lim),np.sum(Oct_sav_lim),np.sum(Nov_sav_lim),np.sum(Dic_sav_lim)]   
    array_de_demd=[np.sum(Ene_demd),np.sum(Feb_demd),np.sum(Mar_demd),np.sum(Abr_demd),np.sum(May_demd),np.sum(Jun_demd),np.sum(Jul_demd),np.sum(Ago_demd),np.sum(Sep_demd),np.sum(Oct_demd),np.sum(Nov_demd),np.sum(Dic_demd)]
    array_de_fraction=[np.sum(Ene_frac),np.sum(Feb_frac),np.sum(Mar_frac),np.sum(Abr_frac),np.sum(May_frac),np.sum(Jun_frac),np.sum(Jul_frac),np.sum(Ago_frac),np.sum(Sep_frac),np.sum(Oct_frac),np.sum(Nov_frac),np.sum(Dic_frac)]   

    return array_de_meses_lim,array_de_demd,array_de_fraction

    
def savingsMonths(sender,ressspiReg,Q_prod_lim,Demand,fuel_cost,boiler_eff,lang,plotPath,imageQlty):    
    array_de_meses_lim,array_de_demd,array_de_fraction=arrays_Savings_Month(Q_prod_lim,Demand,fuel_cost,boiler_eff)
  
    output2=pd.DataFrame(array_de_fraction)
    output2.columns=['Fraccion']
    output3=pd.DataFrame(array_de_demd)
    output3.columns=['Demanda']
    output4=pd.DataFrame(array_de_meses_lim)
    output4.columns=['Ahorro mensual']
    output_excel=pd.concat([output3,output4], axis=1)
    

    meses=["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dec"]
    meses_index=np.arange(0,12)
    fig,ax = plt.subplots()
    
    if ressspiReg==-2:
        fig.patch.set_alpha(0)
    if lang=="spa":
        meses=["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dec"]
        fig.suptitle('Ahorro solar', fontsize=14, fontweight='bold')
        ax.set_ylabel('Ahorro solar en €',color = 'blue') 
        ax.bar(meses_index, output3['Demanda'], width=0.8, color='#362510',label="Demanda")
        ax.bar(meses_index, output4['Ahorro mensual'], width=0.8, color='blue',label="Ahorro solar")
        plt.legend(loc=9, bbox_to_anchor=(0.5, -0.05), ncol=3)     
        ax2 = ax.twinx()          
        ax2 .plot([0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5], output2['Fraccion'],'-',color = 'red',label="% Ahorro",linewidth=2.0)
        ax2.set_ylabel('% de Ahorro',color = 'red')    
        ax.set_xticks(meses_index+.4)  # set the x ticks to be at the middle of each bar since the width of each bar is 0.8
        ax.set_xticklabels(meses)  #replace the name of the x ticks with your Groups name 
        plt.legend(loc='upper right', borderaxespad=0.,frameon=True)

    if lang=="eng":
        meses=["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dec"]
        fig.suptitle('Ahorro solar', fontsize=14, fontweight='bold')
    
        ax.bar(meses_index, output3['Demanda'], width=0.8, color='#362510',label="Demanda")
        ax.bar(meses_index, output4['Ahorro mensual'], width=0.8, color='blue',label="Ahorro solar")
        plt.legend(loc=9, bbox_to_anchor=(0.5, -0.05), ncol=3)     
        ax2 = ax.twinx()          
        ax2 .plot([0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5], output2['Fraccion'],'-',color = 'red',label="% Ahorro",linewidth=2.0)
        ax2.set_ylabel('% de Ahorro',color = 'red')    
        ax.set_xticks(meses_index+.4)  # set the x ticks to be at the middle of each bar since the width of each bar is 0.8
        ax.set_xticklabels(meses)  #replace the name of the x ticks with your Groups name 
        plt.legend(loc='upper right', borderaxespad=0.,frameon=True)
      
    
    if ressspiReg==-2:
        f = io.BytesIO()           # Python 3
        plt.savefig(f, format="png", facecolor=(0.95,0.95,0.95))
        plt.clf()
        image_base64 = base64.b64encode(f.getvalue()).decode('utf-8').replace('\n', '')
        f.close()
        return image_base64
    if ressspiReg==-1:
        fig.savefig(str(plotPath)+'savMonths.png', format='png', dpi=imageQlty)  
    if ressspiReg==0:
        plt.show()
        return output_excel


Q_prod_lim=[35]*8760      
Demand=[55]*8760 
savingsMonths('solatom',0,Q_prod_lim,Demand,0.05,0.8,'spa','',200)    
