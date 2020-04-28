from cov19_local import load_RKI, plot_corona, plot_DT, docu

import numpy as np

date = '2020-04-28'

# County ID for Bavaria - Landkreis ID fuer Bayern
LK_ID = np.array(['09771', '09171', '09371', '09571', '09671', '09772', '09672',
       '09173', '09471', '09472', '09172', '09372', '09473', '09174',
       '09271', '09773', '09279', '09779', '09175', '09176', '09177',
       '09572', '09474', '09178', '09272', '09179', '09573', '09180',
       '09774', '09674', '09475', '09273', '09675', '09476', '09477',
       '09181', '09274', '09478', '09776', '09677', '09182', '09676',
       '09183', '09184', '09775', '09185', '09373', '09575', '09374',
       '09574', '09780', '09777', '09275', '09186', '09276', '09375',
       '09673', '09187', '09576', '09277', '09376', '09678', '09188',
       '09278', '09377', '09189', '09778', '09190', '09577', '09479',
       '09679', '09361', '09561', '09661', '09761', '09461', '09462',
       '09463', '09562', '09563', '09464', '09161', '09762', '09763',
       '09261', '09764', '09162', '09564', '09262', '09362', '09163',
       '09565', '09662', '09263', '09363', '09663'])

# creating a dict for the doubleling time entries
DT = {}

# loop over all counties - Ausfuehren fuer alle Landkreise
for lkid in LK_ID:
    if True:#if lkid == '09182':## # ## to check only one county - nur fuer einen Landkreis
        
        # load from specific csv file
        num, day, month, name, LK_ids, state = load_RKI('data_RKI/RKI_COVID19_Bayern_' + date + '.csv', lkid, state_name='Bavaria')
        #print 'fall  ', num['fall']
        #print 'tod   ', num['tod']
        #print 'gesund', num['gesund']
        
        # specify capacity of intensive care for the individual counties - Beatmungskapazitaet

        # Kapazitaet Beatmung Landkreis Miesbach
        if lkid == '09182': kapazitaet = [14, 28]
        else: kapazitaet = [None, None]
        
        # create plots for every county - Diagramme fuer alle Landkreise  
        DT[lkid] = plot_corona(num, day, month, name=name, ID=lkid, 
                               geraet_min=kapazitaet[0], geraet_max=kapazitaet[1], anteil_beatmung=0.05)

# doubeling time plot - Verdopplungszeitdiagramm
plot_DT(DT, state)

# print out for documentation
docu(LK_ID, DT)
    
    
    
    