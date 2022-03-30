import pandas as pd

## El ángulo de incidencia se debe obtener previamente, por ahora lo introduzco a mano
print("Ángulo de incidencia (en º):")
anguloinput=round(float(input()),1)

## Adicional, elegir con qué coeficientes se quiere calcular el IAM
print("Calcular el IAM a partir de los coeficientes dados por:")
print("1. SAM Default")
print("2. SOLATOM Coeff")
print("3. SOLATOM Real")
print("4. Antiguos SOLATOM Coeff")
coefinput=int(input())
    
def IAM_function(angulo, coef):
    
    ## Asignar a una variable los datos de SAM_IAMS.csv, calculados en Excel mediante los coeficientes que utiliza SAM
    SAM_IAMs_df=pd.read_csv("src/shipcal/collectors/SAM_IAMs.csv")
    print(SAM_IAMs_df)
    
    if coef==1:
        iamtransv=SAM_IAMs_df.loc[10*angulo,'IAM_transv SAM']
        iamlog=SAM_IAMs_df.loc[10*angulo,'IAM_log SAM']
        
    elif coef==2:
        iamtransv=SAM_IAMs_df.loc[10*angulo,'IAM_transv SOL']
        iamlog=SAM_IAMs_df.loc[10*angulo,'IAM_log SOL']
        
    elif coef==3:                           ## En este caso los IAMs están disponibles para valores de angulo que van de 5º en 5º. Es necesario interpolar el resultado
        
        angulo_id3=int(round(angulo/5,0))   ## Redondeamos al número entero más próximo al índice del ángulo para el cual hay un valor de IAM
        dif_ang=angulo-(angulo_id3*5)
        
        if dif_ang<0:                       ## Hemos redondeado hacia arriba, interpolamos con el valor actual y el anterior
            
            a1=SAM_IAMs_df.loc[angulo_id3,'IAM_transv SOL_real']
            a2=SAM_IAMs_df.loc[angulo_id3-1,'IAM_transv SOL_real']
            iamtransv=a1+((a1-a2)/5)*dif_ang
            
            b1=SAM_IAMs_df.loc[angulo_id3,'IAM_log SOL_real']
            b2=SAM_IAMs_df.loc[angulo_id3-1,'IAM_log SOL_real']
            iamlog=b1+((b1-b2)/5)*dif_ang
        
        elif dif_ang>0:                     ## Hemos redondeado hacia abajo, interpolamos con el valor actual y el siguiente
            
            a1=SAM_IAMs_df.loc[angulo_id3,'IAM_transv SOL_real']
            a2=SAM_IAMs_df.loc[angulo_id3+1,'IAM_transv SOL_real']
            iamtransv=a1+((a2-a1)/5)*dif_ang
            
            b1=SAM_IAMs_df.loc[angulo_id3,'IAM_log SOL_real']
            b2=SAM_IAMs_df.loc[angulo_id3+1,'IAM_log SOL_real']
            iamlog=b1+((b2-b1)/5)*dif_ang
            
        elif dif_ang==0:
            iamtransv=SAM_IAMs_df.loc[angulo_id3,'IAM_transv SOL_real']
            iamlog=SAM_IAMs_df.loc[angulo_id3,'IAM_log SOL_real']
    
    elif coef==4:
        iamtransv=SAM_IAMs_df.loc[10*angulo,'IAM_transv SOL_old']
        iamlog=SAM_IAMs_df.loc[10*angulo,'IAM_log SOL_old']
    
    return iamtransv, iamlog, iamtransv*iamlog

IAM=IAM_function(anguloinput,coefinput)

print('\nValor de IAM, calculado según el método:'+str(coefinput))
print('IAM_transv   IAM_log     IAM')
print(IAM)