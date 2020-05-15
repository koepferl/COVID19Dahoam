from pylab import *

####################################
# Load of Input Data (Daten laden) #
####################################

def load_RKI(filename, LandkreisID, state_name ='Bavaria'):  
    '''
    Reads file of the RKI database and selects the relevant data for the specific county.
    
    Input
    =====
    
    filename : str
                path to '*.csv' file downloaded from the RKI.
    
    LandkreisID : str
                String with 5 number entries to select the specific county.
    
    state_name : str, default = 'Bavaria'
                Name of the state.
    
    return
    ======
    
    dic :  dictionary {'fall': array, 'tod':array, 'gesund': array}
           Array of cumulative number of cases
    
    uday :  np.array
            Individual days of notification to the RKI
    
    umonth : np.array
            Individual month of notification to the RKI
    
    region_name : str
            Name of specific region

    dic_LK : dict={'name', 'ID'}
            Alphabetical sorted names of counties and corresponding IDs
    
    state : li[dat_state, num_state, name_state]
            List of dates, cumulative case numbers and state name
    
    '''
    
    import numpy as np
    daten_RKI = np.loadtxt(filename, 
                           skiprows=1, 
                           delimiter=',', 
                           usecols=(9,3,8,6,7,-3),
                           dtype={'names': ('lkID', 'lk_name', 'datum', 'fall', 'tod', 'gesund'), 'formats': ( 'S6', 'S40', 'S10', 'i4', 'i4', 'i4')})
    
    
    # state average
    dat_state = np.unique(daten_RKI['datum'])
    case_state = []
    #tod_state = []
    #gesund_state = []
    
    for dat in dat_state:
        case_state_dat = daten_RKI['fall'][daten_RKI['datum'] == dat]
        #tod_state_dat = daten_RKI['tod'][daten_RKI['datum'] == dat]
        #gesund_state_dat = daten_RKI['gesund'][daten_RKI['datum'] == dat]
        case_state.append(np.sum(case_state_dat))#[case_state_dat > 0]))
    num_state = np.cumsum(np.array(case_state))
    
    # select unique region
    indexes = np.unique(daten_RKI['lkID'], return_index=True)[1]
    uID = daten_RKI['lkID'][indexes]
    u_index_name = daten_RKI['lk_name'][indexes]
    
    # sort and put to dic
    sort_index = np.argsort(u_index_name)
    dic_LK = {'name': u_index_name[sort_index], 'ID': uID[sort_index]}
    
    # rename umlaut
    for i in range(len(dic_LK['name'])):
    
        dic_LK['name'][i] = dic_LK['name'][i].replace('\xc3\xb6', 'oe')
        dic_LK['name'][i] = dic_LK['name'][i].replace('\xc3\x83\xc2\xb6', 'ae')
        dic_LK['name'][i] = dic_LK['name'][i].replace('\xc3\xa4', 'ae')
        dic_LK['name'][i] = dic_LK['name'][i].replace('\xc3\xbcr', 'ue')
        dic_LK['name'][i] = dic_LK['name'][i].replace('\xc3\x83\xc2\xbc', 'ue')
        dic_LK['name'][i] = dic_LK['name'][i].replace('\xc3\xbc', 'ue')
        dic_LK['name'][i] = dic_LK['name'][i].replace('\xc3\x9f', 'ss')
        dic_LK['name'][i] = dic_LK['name'][i].replace('\xc3\x83\xc5\xb8', 'ss')
    
    daten_RKI = daten_RKI[daten_RKI['lkID'] == LandkreisID]
    region_name = dic_LK['name'][dic_LK['ID'] == LandkreisID][0]
    
    print 'region_name loaded', region_name 
    
    # splitting date
    year = np.zeros(len(daten_RKI['datum'])).astype('int')
    month = np.zeros(len(daten_RKI['datum'])).astype('int')
    day = np.zeros(len(daten_RKI['datum'])).astype('int')
    
    dat_sting = daten_RKI['datum']
    for i in range(len(dat_sting)):
        li = dat_sting[i].split('/')
        year[i] = int(li[0])
        month[i] = int(li[1])
        day[i] = int(li[2])
    
    
    # sum up unique dates
    from astropy.table import Table
    RKI_tab = Table([daten_RKI['datum'], year, month, day, daten_RKI['fall'], daten_RKI['tod'], daten_RKI['gesund']],
                    names=('datum', 'year', 'month', 'day', 'fall', 'tod', 'gesund'))
    
    #print RKI_tab
    
    udate = np.unique(RKI_tab['datum'])
    uday = np.zeros(shape=udate.shape)
    umonth = np.zeros(shape=udate.shape)
    uyear = np.zeros(shape=udate.shape)
    ufall = np.zeros(shape=udate.shape)
    utod = np.zeros(shape=udate.shape)
    ugesund = np.zeros(shape=udate.shape)
    
    #print RKI_tab['datum']
    
    for i in range(len(udate)):
        cond = (RKI_tab['datum'] == udate[i])

        fall_day = RKI_tab['fall'][cond]
        #print fall_day[fall_day < 0]
        ufall[i] = np.sum(fall_day)#[fall_day > 0])
        
        tod_day = RKI_tab['tod'][cond]
        utod[i] = np.sum(tod_day)#[tod_day > 0])
        #print tod_day[tod_day < 0]
        
        gesund_day = RKI_tab['gesund'][cond]
        ugesund[i] = np.sum(gesund_day)#[gesund_day > 0])
        #print gesund_day[gesund_day < 0]
        
        uday[i] = RKI_tab['day'][cond][0]
        umonth[i] = RKI_tab['month'][cond][0]
        uyear[i] = RKI_tab['year'][cond][0]
        
    return {'fall': np.cumsum(ufall), 'tod': np.cumsum(utod), 'gesund':np.cumsum(ugesund)}, uday, umonth, region_name, dic_LK, [num_state, dat_state, state_name]#, uyear, udate

##################################################################################################
# Logarithmic Plot of Cumulative Cases (Logarithmische Darstellung der aufsummierten Fallzahlen) #
##################################################################################################

def get_people_of_county(asked_ID, filename = 'data_RKI/12411-001.csv'): 
    import numpy as np

    EW_ID, EW = np.loadtxt(filename, delimiter=';', 
                       usecols=(0, -1), unpack=True, 
                       dtype={'names': ('EW_ID', 'EW'), 'formats': ( 'S10', 'i4')})
    
    ID_str = asked_ID[1:]
    return EW[EW_ID == ID_str][0]



def plot_corona(num_dic, day, month, name, ID, geraet_min=None, geraet_max=None, anteil_beatmung=0.05):
    '''
    Plots cumulative case numbers against time for the specific county. Fits for any dataset 
    larger than eight a exponential function and estimates the doubling time. For the fit only 
    the last eight data points are used to get a recent description of the evolution. Estimates the 
    the doubling time from every fit by taking the fitting constants b of the ``y = a * exp(b * x)``
    underlying theory into account::
    
    ``DT = ln(2)/b``
    
    Input
    =====
    
    num_dic :  dictionary {'fall': array, 'tod':array, 'gesund': array}
           Array of cumulative number of cases
    
    day : np.array
          String with 5 number entries to select the specific county.
    
    name : str
            Name of specific region
    
    ID : str 
            ID of county in Germany e.g. '09182' for LK Miesbach

    geraet_min : int, None
            Minimum capacity of intensive care

    geraet_max : int, default = None
            Maximum capacity of intensive care
    
    anteil_beatmung : float, default = 0.05
            Approximated fraction of demand for intensive care

    return
    ======
    
    DT : list
        Contains name of county, day array and DT array containing the 8 last data points 
        where fit was possible
    
        name : str
            Name of specific region
    
        day : np.array
            Array of 8 days before and including the fit day
    
        val_DT : list
            list containing the calculated day-depending doubling times
    
        rates : list
            list containing rates (mortality rate, recovery rate, still ill rate)
    
        pass_all : dict
            dictionary of daily values of new cases, deaths and recovered cases
    '''
    import matplotlib.pyplot as plt
    import numpy as np
    from scipy.optimize import curve_fit
    
    print '-' * 30
    print name
    print '-' * 30
    
    num = num_dic['fall'][num_dic['fall'] > 0]
    num_tod = num_dic['tod'][num_dic['fall'] > 0]
    num_gesund = num_dic['gesund'][num_dic['fall'] > 0]
    
    day = day[num_dic['fall'] > 0]
    month = month[num_dic['fall'] > 0]
    day_max = 80.
    
    
    fig, ax = plt.subplots(4, figsize=(10,22), gridspec_kw={'height_ratios': [3, 1, 1, 1]})
            
    ax[0].set_title(name + ' (#' + ID +')')
    ax[0].axis([13, day_max, 0.9, 1e5])
    
    ax[0].set_title('Abb. 1', loc='right', fontsize=8)
    ax[1].axis([13, day_max, 0.8, 1e3])
    ax[1].set_title('Abb. 2', loc='right', fontsize=8)
    ax[2].set_xlim([13, day_max])
    ax[2].set_title('Abb. 3', loc='right', fontsize=8)
    ax[3].set_xlim([13, day_max])
    ax[3].set_title('Abb. 4', loc='right', fontsize=8)
    
    
    ####
    # move to March time frame
    #########
    day_real = np.copy(day)
    day[month == 2] = day[month == 2] - 29
    day[month == 1] = day[month == 1] - 29 - 31
    day[month == 4] = day[month == 4] + 31
    day[month == 5] = day[month == 5] + 31 + 30
    
    #print 'day now', day
    #print 'day_real', day_real
    
    #########
    # fit
    #########
    def func(x, a, b):#, c):
        #return a * np.exp(b * x)# + c #
        #return a * b**(c*x)
        return np.log(a) + b * x  #log-linear
    
    x = np.arange(10,day_max,0.5)
    
    # fit only when there are more than 6 data points and cases every day.
    data_points = range(8, len(day)+1)
    
    DTs = []
    Ntot_today = []
    Ntot_week = []
    R4s = []
    
    col = 30
    colapp = []
    print 'Tag  DTs  R4'
    for cut in data_points:
        #print day[cut-8:cut]
        #print num[cut-8:cut]
        
        #########        
        ### changed 8 fit
        #########
        #popt, pcov = curve_fit(func, day[:cut], num[:cut])
        popt, pcov = curve_fit(func, day[cut-8:cut], np.log(num[cut-8:cut]))
        #print len(day[cut-8:cut])
        
        #####
        # loglog
        cond_week = day[cut-8:cut] > day[cut-1] - 7
        num_week = num[cut-8:cut][cond_week]
        
        Ntot_today.append(num[cut-8:cut][-1])
        Ntot_week.append(num_week[-1] - num_week[0])
        
        ########
        # Reproduction number for Rtime notification days (4 days strict)
        
        #%%%%%%%%#daytoday = int(day[cut-1])
        #%%%%%%%%#dayminus4 = int(daytoday - 5)
        #%%%%%%%%#dayminus8 = int(daytoday - 9)
        #%%%%%%%%#print daytoday, dayminus4, dayminus8
        #%%%%%%%%#
        #%%%%%%%%#print num[day == daytoday], num[day == dayminus4], num[day == dayminus8]
        #%%%%%%%%#
        #%%%%%%%%#R4_row = (num[day == daytoday] - num[day == dayminus4]) / (num[day == dayminus4] - num[day == dayminus8])
        #%%%%%%%%#print R4_row
        #%%%%%%%%#
        #%%%%%%%%#raise Exception('stop')
        
        ########
        # Reproduction number for Rtime notification days
        #print num[cut-8:cut]
        
        if cut-9 < 0:
            num_before_int = num[cut-8:cut][0]
        else: num_before_int = num[cut-8] - num[cut-9]
        num_diff_8 = np.append(num_before_int, np.diff(num[cut-8:cut]))
        #print num_diff_8
        
        R4 = np.sum(num_diff_8[4:]) / np.sum(num_diff_8[0:4])
        R4s.append(R4)
        #print num_diff_8[0:4], num_diff_8[4:]
        
        #########
        # doubling time
        #########
        DT = np.round(np.log(2) / popt[1],2)
        #print DT#,  popt
        DTs.append(DT)
        #print popt, np.log(2) / popt[1]

        print '%02d'%int(day_real[cut-1]) + '.' +  '%02d'%int(month[cut-1]), '%6.2f'%DT#, '%6.2f'%R4

        #print("a =", popt[0], "+/-", pcov[0,0]**0.5)
        #print("b =", popt[1], "+/-", pcov[1,1]**0.5)
        #print("c =", popt[2], "+/-", pcov[2,2]**0.5)
    
        ##########
        # plot
        ##########
        
        
        ########
        # plot fit
        #########
        day_label = 'Fit am ' + '%02d'%int(day_real[cut-1]) + '.' + '%02d'%int(month[cut-1]) + '; VZ: ' + '%6.2f'%DT + ' d'
        ax[0].semilogy(x, np.exp(func(x, *popt)), '-', color=plt.cm.viridis(int(col)), 
                     label=day_label)
        
        colapp.append(int(col))
        col = col + 256 / len(data_points)         

        ########
        # plot Beatmungsbedarf        
        #########
        if cut == data_points[-1]:
            
            # Beatmungsampel
            bedarf =  anteil_beatmung * np.exp(func(x, *popt))
            
            ax[0].semilogy(x, bedarf, 
                         '-', lw=3, color=plt.cm.Reds(200), 
                         label='Ampel (Beatmungsbedarf ca. ' + str(int(anteil_beatmung*100)) + '%)')
            ax[0].semilogy(x[(bedarf < geraet_max)],bedarf[(bedarf < geraet_max)], 
                         '-', lw=3, color=plt.cm.jet(180), 
                         label='Ampel (Beatmungsbedarf ca. ' + str(int(anteil_beatmung*100)) + '%)')
            ax[0].semilogy(x[bedarf < geraet_min],bedarf[bedarf < geraet_min], 
                         '-', lw=3, color=plt.cm.Greens(200), 
                         label='Ampel (Beatmungsbedarf ca. ' + str(int(anteil_beatmung*100)) + '%)')
            
            # Fehler
            ax[0].semilogy(x, 0.05*np.exp(func(x, 
                                 popt[0] - pcov[0,0]**0.5, 
                                 popt[1] - pcov[1,1]**0.5)), 
                                 #popt[2] - pcov[2,2]**0.5), 
                         '--', color='k', alpha=0.5, label='Unsicherheiten')
            ax[0].semilogy(x, 0.05*np.exp(func(x, 
                                 popt[0] + pcov[0,0]**0.5, 
                                 popt[1] + pcov[1,1]**0.5)), 
                                 #popt[2] + pcov[2,2]**0.5), 
                         '--', color='k', alpha=0.5)
    
    #print 'day now2', day
    
    
    ####
    # Beatmungs Kapazitaet
    #########
    ax[0].plot([x[0], x[-1]], [geraet_min]*2, 'k:', label="Kapazitaet Beatmungsapparate")
    ax[0].plot([x[0], x[-1]], [geraet_max]*2, 'k:')
    
    ####
    # gemeldete Fallzahlen
    #########
    ax[0].semilogy(day, num, 'k+', label="COVID19 erkrankt")
    ax[0].semilogy(day, num_tod, 'k*', label="davon verstorben")
    ax[0].semilogy(day, num_gesund, 'ko', alpha=0.3, label="davon genesen")
    
    #print 'day now3', day
    
    print '+' * 30
    print 'Sterberate (%): ', np.round(num_tod[-1] / num[-1] * 100, 2)
    print 'Gesunde (%):    ', np.round(num_gesund[-1] / num[-1] * 100, 2)
    print '+' * 30
    
    
    
    #############
    # formating
    #############
    
    from matplotlib.ticker import ScalarFormatter
    for axis in [ax[0].xaxis, ax[0].yaxis]:
        axis.set_major_formatter(ScalarFormatter())
    
    ax[0].grid(True, which="both")
    ax[0].set_xticks(np.arange(14, day_max, 2))
    ax[0].set_xticklabels([14, 16, 18, 20, 22, 24, 26, 28, 30, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 1, 3, 5, 7, 9, 11, 13, 15, 17])
    
    ax[0].text(13, 0.4, 'Mar')
    ax[0].text(31, 0.4, 'Apr')
    ax[0].text(31+30, 0.4, 'Mai')
    ax[0].annotate('Ausgangssperre', ha='center', xy=(21, ax[0].get_ylim()[0]), xytext=(21, 0.4), 
                    arrowprops=dict(arrowstyle= '-|>', color='grey', lw=2, ls='-'), alpha=0.6)
    ax[0].annotate('Ostern', ha='center', xy=(31+12, ax[0].get_ylim()[0]), xytext=(31+12, 0.4), 
                    arrowprops=dict(arrowstyle= '-|>', color='grey', lw=2, ls='-'), alpha=0.6)
    ax[0].annotate('Ende Ferien', ha='center', xy=(31+20, ax[0].get_ylim()[0]), xytext=(31+20, 0.4), 
                    arrowprops=dict(arrowstyle= '-|>', color='grey', lw=2, ls='-'), alpha=0.6)
    
    # credit bar
    credit = 'Christine Greif\nhttp://www.usm.uni-muenchen.de/~koepferl\nThis work is licensed under CC-BY-SA 4.0\nData: NPGEO-DE; VZ = Verdopplungszeit'
    loc_label = ax[0].get_xlim()[1] * 1.12
    link = ax[0].text(loc_label, 9e4, credit, fontsize=8, va='top')
    link.set_url('http://www.usm.uni-muenchen.de/~koepferl')
    
    # label
    ax[0].set_ylabel('Gesamte Fallzahlen')
    lgd = ax[0].legend(loc='best', bbox_to_anchor=(1.12, 0.93))
    
    # percent
    #########
    EW_county = get_people_of_county(asked_ID=ID)
    
    axi = ax[0].twinx()
    
    #print 'lim', ax.get_ylim(), ax.get_ylim()[0] / EW_county * 100, ax.get_ylim()[1] / EW_county * 100, EW_county
    axi.set_ylim(ax[0].get_ylim()[0] / EW_county * 100 , ax[0].get_ylim()[1] / EW_county * 100 )
    axi.set_yscale('log')
    import matplotlib.ticker as mtick
    import matplotlib.ticker as ticker
    axi.yaxis.set_major_formatter(ScalarFormatter())
    axi.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y,pos: ('{{:.{:1d}f}}%'.format(int(np.maximum(-np.log10(y),0)))).format(y)))
    #axi.yaxis.set_major_formatter(FormatStrFormatter('%4d'))
    #axi.yaxis.set_major_formatter(mtick.PercentFormatter())
    axi.set_ylabel('Prozentualer Anteil zur Gesamteinwohnerzahl (' + str(EW_county) + ') im Kreis')
    
    ###########
    # plot 2
    ###########
    pass_all = {'day': day, 'fall': np.append(num[0], np.diff(num)), 'gesund': np.append(num_gesund[0], np.diff(num_gesund)), 'tod': np.append(num_tod[0], np.diff(num_tod))}
    
    ax[1].set_ylabel('Taeglich gemeldete Fallzahlen')
    
    # gemittelt ueber 7 Tage
    all_smooth = np.zeros(shape = day[6:].shape)
    tod_smooth = np.zeros(shape = day[6:].shape)
    gesund_smooth = np.zeros(shape = day[6:].shape)

    for z in range(7):
        stop = -6+z
        #print z, stop
        if stop != 0:
            all_smooth =  all_smooth + 1/7. * pass_all['fall'][z:stop]
            tod_smooth = tod_smooth + 1/7. * pass_all['tod'][z:stop]
            gesund_smooth = gesund_smooth + 1/7. * pass_all['gesund'][z:stop]
        else:
            all_smooth =  all_smooth + 1/7. * pass_all['fall'][z:]
            tod_smooth = tod_smooth + 1/7. * pass_all['tod'][z:]
            gesund_smooth = gesund_smooth + 1/7. * pass_all['gesund'][z:]
            
        
    #all_smooth = 0.25 * (pass_all['fall'][0:-3] + pass_all['fall'][1:-2] + pass_all['fall'][2:-1] + pass_all['fall'][3:0])
    #tod_smooth = 0.25 * (pass_all['tod'][0:-3] + pass_all['tod'][1:-2] + pass_all['tod'][2:-1] + pass_all['tod'][3:0])
    #gesund_smooth = 0.25 * (pass_all['gesund'][0:-3] + pass_all['gesund'][1:-2] + pass_all['gesund'][2:-1] + pass_all['gesund'][3:0])
    
    ax[1].semilogy(day[6:], all_smooth, 'r-', label='neu erkrankt (7-Tagesmittel)')
    ax[1].semilogy(day[6:], tod_smooth, 'k-', label='verstorben (7-Tagesmittel)')
    ax[1].semilogy(day[6:], gesund_smooth, 'k-', alpha=0.3, label='genesen (7-Tagesmittel)')
    
    # box
    import matplotlib.patches as patches
    for b in range(len(day)):
        if b == 0:
            label_fall = "neu erkrankt"
            label_gesund = 'genesen'
            label_tod = 'verstorben'
        else:
            label_fall = None
            label_gesund = None
            label_tod = None
        
        
        ax[1].add_patch(patches.Rectangle((day[b]-0.45,0.),0.9,pass_all['fall'][b],
                                          linewidth=1,edgecolor='k',facecolor=plt.cm.jet(180), label=label_fall))           
        ax[1].add_patch(patches.Rectangle((day[b]-0.45,0.),0.9,pass_all['gesund'][b],
        linewidth=1,edgecolor='k',facecolor='None', label=label_gesund, hatch='////'))        
        ax[1].add_patch(patches.Rectangle((day[b]-0.45,0.),0.9,pass_all['tod'][b],
        linewidth=1,edgecolor='k',facecolor='w', label=label_tod))
    
    #h = ax[1].hist(pass_all['fall'], bins=np.append(day - 0.5, day[-1] + 0.5))
    #print h
    #print pass_all['fall']
    #ax[1].hist(pass_all['tod'], bins=day)
    #ax[1].hist(pass_all['gesund'], bins=day)
    
    from matplotlib.ticker import ScalarFormatter
    for axis in [ax[1].xaxis, ax[1].yaxis]:
        axis.set_major_formatter(ScalarFormatter())
    
    ax[1].set_axisbelow(True)
    ax[1].grid(True, which="both")
    ax[1].set_xticks(np.arange(14, day_max, 2))
    ax[1].set_xticklabels([14, 16, 18, 20, 22, 24, 26, 28, 30, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 1, 3, 5, 7, 9, 11, 13, 15, 17])
    
    tx1 = ax[1].text(13, 0.2, 'Mar')
    tx2 = ax[1].text(31, 0.2, 'Apr')
    tx3 = ax[1].text(31+30, 0.2, 'Mai')
    ax[1].annotate('Ausgangssperre', ha='center', xy=(21, ax[1].get_ylim()[0]), xytext=(21, 0.2), 
                    arrowprops=dict(arrowstyle= '-|>', color='grey', lw=2, ls='-'), alpha=0.6)
    ax[1].annotate('Ostern', ha='center', xy=(31+12, ax[1].get_ylim()[0]), xytext=(31+12, 0.2), 
                    arrowprops=dict(arrowstyle= '-|>', color='grey', lw=2, ls='-'), alpha=0.6)
    ax[1].annotate('Ende Ferien', ha='center', xy=(31+20, ax[1].get_ylim()[0]), xytext=(31+20, 0.2), 
                    arrowprops=dict(arrowstyle= '-|>', color='grey', lw=2, ls='-'), alpha=0.6)
        
    ax[1].legend(loc='best')
    
    ###########
    # plot 3
    ###########
    ax[2].set_ylabel('Verdopplungszeiten in Tage')
    ax[2].plot(ax[2].get_xlim(), [10,10], ':', lw =2, color='grey', label='VZ = 10') 
    ax[2].plot(day[7:], np.array(DTs), 'k.-') 
    
    #from scipy.signal import find_peaks
    #peaks, _ = find_peaks(np.array(DTs))
    #print 'peaks', peaks
    #ax[2].plot(peaks, np.array(DTs)[peaks], "Hb")
    
    #ax[2].plot(day[7:], np.gradient(DTs, day[7:]), 'ko-')
    diff = np.diff(DTs)
    ax[2].plot(day[7:][1:][diff < 0], np.array(DTs)[1:][diff < 0], '^', color=plt.cm.Reds(200), label='Achtung: VZ faellt (!!!)') 
    #ax[2].plot(day[7:][1:], diff, 'k^-')
    
    #print 'gradient', gradient
    #print 'diff', np.diff(DTs)
    
    ax[2].grid(True, which="both")
    ax[2].set_xticks(np.arange(14, day_max, 2))
    ax[2].set_xticklabels([14, 16, 18, 20, 22, 24, 26, 28, 30, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 1, 3, 5, 7, 9, 11, 13, 15, 17])
    
    ax[2].legend(loc='best')
    offset = ax[2].get_ylim()[0] - (ax[2].get_ylim()[1] - ax[2].get_ylim()[0]) / 5.
    tx1 = ax[2].text(13, offset, 'Mar')
    tx2 = ax[2].text(31, offset, 'Apr')
    tx3 = ax[2].text(31+30, offset, 'Mai')
    ax[2].annotate('Ausgangssperre', ha='center', xy=(21, ax[2].get_ylim()[0]), xytext=(21, offset), 
                    arrowprops=dict(arrowstyle= '-|>', color='grey', lw=2, ls='-'), alpha=0.6)
    ax[2].annotate('Ostern', ha='center', xy=(31+12, ax[2].get_ylim()[0]), xytext=(31+12, offset), 
                    arrowprops=dict(arrowstyle= '-|>', color='grey', lw=2, ls='-'), alpha=0.6)
    ax[2].annotate('Ende Ferien', ha='center', xy=(31+20, ax[2].get_ylim()[0]), xytext=(31+20, offset), 
                    arrowprops=dict(arrowstyle= '-|>', color='grey', lw=2, ls='-'), alpha=0.6)
    
    
    ###########
    # plot 4
    ###########
    
    ########
    # Reproduction number for Rtime notification days (4 days interpoliert)
    
    minus8 = np.interp(day-8-1, day, num)
    minus4 = np.interp(day-4-1, day, num)
    minus_all = np.interp(np.arange(day[0], day[-1]), day, num)
    #print day - 8 - 1
    #print day
    #print num
    #print day - 4 - 1
    
    #for i in range(len(np.arange(day[0], day[-1]))):
    #    print np.arange(day[0], day[-1])[i], minus_all[i]
    
    R_number_interp = (num - minus4) / (minus4 - minus8)
    R_number_interp[day-8-1 < day[0]] = np.nan # before 1st case
    R_number_interp[day-4-1 < day[0]] = np.nan # before 1st case
    
    
    #for da in day:
    #    if da-4 < day[0]:
    #        new_minus4 = 0
    #    else: new_minus4 = np.interp(da-4, day, num)
    #    if da-8 < day[0]:
    #        new_minus8 = 0
    #    else:
    #        new_minus8 = np.interp(da-8, day, num)
    
    ax[3].set_ylabel('Interpolierte Reproduktionszahl')
    
    ax[3].plot(ax[3].get_xlim(), [1,1], ':', lw =2, color='grey', label='R = 1') 
    ax[3].plot(day, R_number_interp, 'k.-') 
    ax[3].plot(day[R_number_interp >= 1], R_number_interp[R_number_interp >= 1], '^', color=plt.cm.Reds(200), label='Achtung: R > 1 (!!!)') 
    
    ax[3].grid(True, which="both")
    ax[3].set_xticks(np.arange(14, day_max, 2))
    ax[3].set_xticklabels([14, 16, 18, 20, 22, 24, 26, 28, 30, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 1, 3, 5, 7, 9, 11, 13, 15, 17])
    ax[3].legend(loc='best')
    
    offset = ax[3].get_ylim()[0] - (ax[3].get_ylim()[1] - ax[3].get_ylim()[0]) / 5.
    tx1 = ax[3].text(13, offset, 'Mar')
    tx2 = ax[3].text(31, offset, 'Apr')
    tx3 = ax[3].text(31+30, offset, 'Mai')
    ax[3].annotate('Ausgangssperre', ha='center', xy=(21, ax[3].get_ylim()[0]), xytext=(21, offset), 
                    arrowprops=dict(arrowstyle= '-|>', color='grey', lw=2, ls='-'), alpha=0.6)
    ax[3].annotate('Ostern', ha='center', xy=(31+12, ax[3].get_ylim()[0]), xytext=(31+12, offset), 
                    arrowprops=dict(arrowstyle= '-|>', color='grey', lw=2, ls='-'), alpha=0.6)
    ax[3].annotate('Ende Ferien', ha='center', xy=(31+20, ax[3].get_ylim()[0]), xytext=(31+20, offset), 
                    arrowprops=dict(arrowstyle= '-|>', color='grey', lw=2, ls='-'), alpha=0.6)

    ax[3].text(ax[3].get_xlim()[1] * 1.02, 
               ax[3].get_ylim()[1] * 1.,
               'zu Abb. 1: \nBei Kreisen mit sehr kurzen Verdopplungszeiten wird \nder Verlauf nicht/kaum flacher; mit sehr langen \nVerdopplungszeiten (wenigen Neuerkrankten) \nist der Verlauf fast horizontal. \n(Ziel: horizontale Linie).')
    
    ax[3].text(ax[3].get_xlim()[1] * 1.02, 
               ax[3].get_ylim()[1] * 0.75, 
               'zu Abb. 2: \nBalkendiagramm der taeglich gemeldeten Fallzahlen. \n(Ziel: keine gelben und weissen Balken.)'
               )
       
    ax[3].text(ax[3].get_xlim()[1] * 1.02,
               ax[3].get_ylim()[1] * 0.35, 
               'zu Abb. 3: \nVerdopplungszahl gibt die Zeit an in der sich die \nFallzahlen verdoppeln. Verdopplungszeiten kleiner \nals 10 oder abnehmend sind bedenklich. \n(Ziel: keine verkuerzenden Verdopplungszeiten \nund viel groesser als 10).'
               )
    
    ax[3].text(ax[3].get_xlim()[1] * 1.02, 
               ax[3].get_ylim()[0], 
               'zu Abb. 4: \nReproduktionszahl gibt die Anzahl der \nWeiteransteckungen durch einen Infizierten an. \nReproduktionszahl groesser als 1 ist bedenklich. \n(Ziel: Reproduktionszahl viel kleiner als 1).'
               )
    
    fig.savefig('expert/' + name + '_expert.pdf', dpi=300, overwrite=True, bbox_inches='tight', bbox_extra_artists=(lgd, tx1, tx2))
    
    
    ##################
    # save plot ax[0]
    ##################
    
    ax[1].remove()
    ax[2].remove()
    ax[3].remove()
    #for a in ax:
    #    print 'ax'
    #fig.set_size_inches(10, 8)
    #ax[0].set_aspect(aspect=0.5)
    #fig.set_gridspec_kw({'height_ratios': [1, 0, 0, ]})
    #fig.gridspec_kw({'height_ratios': [1]})
    
    #extent = ax[0].get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    # Pad the saved area by 10% in the x-direction and 20% in the y-direction
    fig.savefig('plots/' + name + '.pdf', dpi=300, overwrite=True, bbox_extra_artists=(lgd, tx1, tx2, tx3), bbox_inches='tight')
                    
    rates = {'death_rate': num_tod / num * 100, 
             'recover_rate': num_gesund / num * 100, 
             'ill_rate': (num - num_gesund - num_tod) / num * 100,
              'day': day}
              
    
    return [name, day[7:], DTs, Ntot_today, Ntot_week, rates, R4s, pass_all]

#####################################
# Doubeling Time (Verdopplungszeit) #
#####################################

def plot_DT(DT, state, ncol=4, nrow=3):
    '''
    Plots day-dependent doubling time against time for the selected counties.
    
    input
    ======
    
    DT : list
        Contains name of county, day array and DT array containing the 8 last data-points 
        where fit was possible
    
        name : str
            Name of specific region
    
        day : np.array
            Array of 8 days before and including the fit day
    
        val_DT : list
            list containing the calculated day-depending doubling times
    
        rates : list
            list containing rates (mortality rate, recovery rate, still ill rate)
    
    
    state : list
            output from load_RKI
    
    ncol : int
        Number of columns in plot (should not be changed for now.)

    nrow : int
        Number of rows in plot (should not be changed for now.)
    
    returns
    =======
    
    Saves diagram as PDF.
    
    '''
    ######################################
    # DT for state
    #######################
    
    ####
    # move to March time frame
    #########
    
    day_max = 80.
    
    dat_states = state[1]
    
    state_day = []
    for i in range(len(dat_states)):
        y, m, d = dat_states[i].split('/')
        if m == '01': state_day.append(int(d) - 29 - 31)
        if m == '02': state_day.append(int(d) - 29)
        if m == '03': state_day.append(int(d))
        if m == '04': state_day.append(int(d) + 31) 
        if m == '05': state_day.append(int(d) + 31 + 30) 
    
    #########
    # fit
    #########
    def func(x, a, b):#, c):
        #return a * np.exp(b * x)# + c
        #return a * b**(c*x)
        return np.log(a) + b * x
    
    x = np.arange(10,day_max,0.5)
    
    # fit only when there are more than 8 data points and cases every day.
    data_points = range(8, len(state_day)+1)
    state_day = np.array(state_day)
    state_num = np.array(state[0])
    DTs_state = []
    
    from scipy.optimize import curve_fit
    for cut in data_points:
        popt, pcov = curve_fit(func, state_day[cut-8:cut], np.log(state_num[cut-8:cut]))
        
        #########
        # doubling time
        #########
        DT_state = np.round(np.log(2) / popt[1],2)
        DTs_state.append(DT_state)

    fig, axs = plt.subplots(nrow, ncol, figsize=(28,21))
    fig2, axs2 = plt.subplots(nrow, ncol, figsize=(28,21))
    fig3, axs3 = plt.subplots(nrow, ncol, figsize=(28,21))
    fig4, axs4 = plt.subplots(nrow, ncol, figsize=(28,21))
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.1, hspace=0.1)
    axs[0,0].set_title('Entwicklung der Verdopplungszeiten auf Kreisebene')
    axs[0,1].set_title('Evolution of the Doubeling Time for German Counties')
    axs[0,2].set_title('Entwicklung der Verdopplungszeiten auf Kreisebene')
    axs[0,3].set_title('Evolution of the Doubling Time for German Counties')


    
    print len(DT.keys())
    
    # sort after Landkreis name not ID
    DT_ids = DT.keys()
    
    DT_names = []
    for key in DT_ids:
        DT_names.append(DT[key][0])
        print key, DT[key][0]
        
    DT_ids = np.array(DT_ids)
    DT_names = np.array(DT_names)
    
    DT_index = np.argsort(DT_names)
    DT_ids = DT_ids[DT_index]
    DT_names = DT_names[DT_index]
    
    
    #print '*' * 10
    #print DT_names[95], DT_ids[95]
    
    sorted_keys = DT_ids
    
    from matplotlib.cm import get_cmap
    cmap = get_cmap('inferno')  # type: matplotlib.colors.ListedColormap
    
    for i in range(len(sorted_keys)):
        
        if i in range(0, 8): 
            ax = axs[0,0]
            ax2 = axs2[0,0]
            ax3 = axs3[0,0]
            ax4 = axs4[0,0]
            line_col = 20 + 30 * (8 - i)

        if i in range(8, 16): 
            ax = axs[0,1]
            ax2 = axs2[0,1]
            ax3 = axs3[0,1]
            ax4 = axs4[0,1]
            line_col = 20 + 30 * (16 - i)

        if i in range(16,24): 
            ax = axs[0,2]
            ax2 = axs2[0,2]
            ax3 = axs3[0,2]
            ax4 = axs4[0,2]
            line_col = 20 + 30 * (24 - i)

        if i in range(24,32): 
            ax = axs[0,3]
            ax2 = axs2[0,3]
            ax3 = axs3[0,3]
            ax4 = axs4[0,3]
            line_col = 20 + 30 * (32 - i)

        if i in range(32,40): 
            ax = axs[1,0]
            ax2 = axs2[1,0]
            ax3 = axs3[1,0]
            ax4 = axs4[1,0]
            line_col = 20 + 30 * (40 - i)

        if i in range(40,48): 
            ax = axs[1,1]
            ax2 = axs2[1,1]
            ax3 = axs3[1,1]
            ax4 = axs4[1,1]
            line_col = 20 + 30 * (48 - i)

        if i in range(48,56): 
            ax = axs[1,2]
            ax2 = axs2[1,2]
            ax3 = axs3[1,2]
            ax4 = axs4[1,2]
            line_col = 20 + 30 * (56 - i)

        if i in range(56,64): 
            ax = axs[1,3]
            ax2 = axs2[1,3]
            ax3 = axs3[1,3]
            ax4 = axs4[1,3]
            line_col = 20 + 30 * (64 - i)

        if i in range(64,72): 
            ax = axs[2,0]
            ax2 = axs2[2,0]
            ax3 = axs3[2,0]
            ax4 = axs4[2,0]
            line_col = 20 + 30 * (72 - i)

        if i in range(72,80): 
            ax = axs[2,1]
            ax2 = axs2[2,1]
            ax3 = axs3[2,1]
            ax4 = axs4[2,1]
            line_col = 20 + 30 * (80 - i)

        if i in range(80,88): 
            ax = axs[2,2]
            ax2 = axs2[2,2]
            ax3 = axs3[2,2]
            ax4 = axs4[2,2]
            line_col = 20 + 30 * (88 - i)

        if i in range(88,96): 
            ax = axs[2,3]
            ax2 = axs2[2,3]
            ax3 = axs3[2,3]
            ax4 = axs4[2,3]
            line_col = 20 + 30 * (96 - i)
            
        key = sorted_keys[i]
        if i in [0, 8 ,16, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96]:
            ax.semilogy(state_day[7:], DTs_state, '.:k', label= state[2] + ' average')
            print '-' * 20
            print state[2], DTs_state[-1], int(state_day[7:][-1])
            print '-' * 20
        
        ax.semilogy(DT[key][1], DT[key][2], '.-', c = cmap(line_col), label=DT[key][0])
        ax2.loglog(DT[key][3], DT[key][4], '.-', c = cmap(line_col), label=DT[key][0])
        print DT[key][2][-1], int(DT[key][1][-1]), DT[key][0]
        
        ax3.plot(DT[key][5]['day'], DT[key][5]['death_rate'], '*-', c = cmap(line_col), label=DT[key][0])
        ax4.plot(DT[key][1], DT[key][6], '.-', c = cmap(line_col), label=DT[key][0])
        #ax3.plot(DT[key][5]['day'], DT[key][5]['recover_rate'], 'o-', c = cmap(line_col), label=DT[key][0])
        #ax3.plot(DT[key][5]['day'], DT[key][5]['ill_rate'], 'x-', c = cmap(line_col), label=DT[key][0])
        
    
    ######
    # axis
    
    #factor_1 = 100/60.
    x_pos = 37
    
    credit2 = 'Christine Greif\nhttp://www.usm.uni-muenchen.de/~koepferl\nThis work is licensed under CC-BY-SA 4.0\nData: NPGEO-DE'
    
    link = axs[2,3].text(x_pos, 0.7, credit2, fontsize=8, va = 'top')    
    link = axs3[2,3].text(x_pos, -2, credit2, fontsize=8)
    link = axs4[2,3].text(x_pos, -1., credit2, fontsize=8)
    link = axs2[2,3].text(3.5, 0.5, credit2, fontsize=8, va='top')
    
    link.set_url('http://www.usm.uni-muenchen.de/~koepferl')

    
    axs[0,0].set_ylabel('Verdopplungszeiten (Tage)')
    axs[1,0].set_ylabel('Doubling Time DT (days)')
    axs[2,0].set_ylabel('Verdopplungszeiten (Tage)')

    
    for ax in axs.reshape(-1):
        ax.set_ylim(1.5,500.9)
        ax.set_xlim(13,day_max)
    
        from matplotlib.ticker import ScalarFormatter
        for axis in [ax.xaxis, ax.yaxis]:
            axis.set_major_formatter(ScalarFormatter())
        ax.grid(True, which="both")

        ax.set_xticks(np.arange(14, day_max, 4))
        ax.set_xticklabels([14, 18, 22, 26, 30, 3, 7, 11, 15, 19, 23, 27, 1, 5, 9, 13, 17])
    
        ax.legend(loc='upper left')
    
        #if ax in [axs[2,0], axs[2,1], axs[2,2], axs[2,3]]:
        ax.text(13, 0.8, 'Maerz/March')
        ax.text(31, 0.8, 'April')
        ax.text(31+30, 0.8, 'Mai/May')
    
            
    for ax2 in axs2.reshape(-1):
        
        from matplotlib.ticker import ScalarFormatter
        for axis in [ax2.xaxis, ax2.yaxis]:
            axis.set_major_formatter(ScalarFormatter())
        ax2.grid(True, which="both")
        
        ax2.set_ylim(1.5,2000)
        ax2.set_xlim(1.5,10000)
        ax2.legend(loc='upper left')
        
        if ax2 in [axs2[2,0], axs2[2,1], axs2[2,2], axs2[2,3]]:
            ax2.set_xlabel('Totale Fallzahlen (total number of cases)')
        if ax2 in [axs2[0,0], axs2[1,0], axs2[2,0]]:
            ax2.set_ylabel('Fallzahlen in der letzten Woche (number of new cases last week)')
        
    for ax3 in axs3.reshape(-1):
        ax3.set_ylim(0,20.9)
        ax3.set_xlim(13,day_max)
    
        ax3.grid(True, which="both")
        ax3.set_xticks(np.arange(14, day_max, 4))
        ax3.set_xticklabels([14, 18, 22, 26, 30, 3, 7, 11, 15, 19, 23, 27, 1, 5, 9, 13, 17])
        
        if ax3 in [axs3[0,0], axs3[1,0], axs3[2,0]]:
            ax3.set_ylabel('Sterberaten in %')
        
    
        ax3.legend(loc='upper left')
    
        #if ax in [axs[2,0], axs[2,1], axs[2,2], axs[2,3]]:
        offset3 = - 0.07 * ax3.get_ylim()[1]
        ax3.text(13, offset3, 'Maerz/March')
        ax3.text(31, offset3, 'April')
        ax3.text(31+30, offset3, 'Mai/May')
        
    
    for ax4 in axs4.reshape(-1):
        ax4.set_ylim(0,4.9)
        ax4.set_xlim(13,day_max)
    
        ax4.grid(True, which="both")
        ax4.set_xticks(np.arange(14, day_max, 4))
        ax4.set_xticklabels([14, 18, 22, 26, 30, 3, 7, 11, 15, 19, 23, 27, 1, 5, 9, 13, 17])
    
        ax4.legend(loc='upper left')
    
        #if ax in [axs[2,0], axs[2,1], axs[2,2], axs[2,3]]:
        offset4 = - 0.07 * ax4.get_ylim()[1]
        ax4.text(13, offset4, 'Maerz/March')
        ax4.text(31, offset4, 'April')
        ax4.text(31+30, offset4, 'Mai/May')
        
        if ax4 in [axs4[1,0]]:
            ax4.set_ylabel('geschaetzte Reproduktionszahl R (Anzahl letzten 4 Meldungen / Anzahl der letzten 4 Meldungen davor)')
        
    
    #plt.show()
    fig.savefig('DT_' + state[2] + '.pdf', dpi=300, overwrite=True, bbox_inches='tight')
    fig2.savefig('loglog_' + state[2] + '.pdf', dpi=300, overwrite=True, bbox_inches='tight')
    fig3.savefig('rate_' + state[2] + '.pdf', dpi=300, overwrite=True, bbox_inches='tight')    
    fig4.savefig('R_' + state[2] + '.pdf', dpi=300, overwrite=True, bbox_inches='tight')    

def docu(LK_ID, DT):
    print '*' * 30
    print 'English Documentation'
    print '*' * 30

    day_print = []
    DT_print = []
    name_print = []
    for lkid in LK_ID:
        #print DT[lkid]
        #print DT[lkid][2]
        DT_print.append(DT[lkid][2][-1])
        day_print.append(DT[lkid][1][-1])
        name_print.append(DT[lkid][0])

    # sort
    asort = np.argsort(DT_print)
    DT_print = np.array(DT_print)[asort]
    day_print = np.array(day_print)[asort]
    name_print = np.array(name_print)[asort]   


    for i in range(len(name_print)):
        if i == 0:
            #print '    * Bavaria average is ' + str(DT['Bavaria'][2][-1]) + 'd'
            print '    * 5 counties with lowest DTS (the larger the better):'
    
        if i == len(name_print) - 6: 
            print '    * 5 counties with highest DTs (the larger the better):'

        if (i < 5) or (i > len(name_print) - 6) :   
            if day_print[i]-31 <= 30: #April
                print '        *', '%6.2f'%DT_print[i], str(int(day_print[i]-31)) + '.4', name_print[i]
            if day_print[i]-31 > 30: #Mai
                print '        *', '%6.2f'%DT_print[i], str(int(day_print[i]-31 - 30)) + '.5', name_print[i]

    print '*' * 30
    print 'German Documentation'
    print '*' * 30

    for i in range(len(name_print)):
        if i == 0:
            #print '    * Bayerischer Durchschnitt mit ' + str(DT['Bavaria'][2][-1]) + 'd'
            print '    * 5 Kreise mit den niedriger Verdopplungszeiten (umso groesser desto besser):'
    
        if i == len(name_print) - 6: 
            print '    * 5 Kreise mit den hoechsten Verdopplungszeiten (umso groesser desto besser):'

        if (i < 5) or (i > len(name_print) - 6) :   
            if day_print[i]-31 <= 30: #April
                print '        *', '%6.2f'%DT_print[i], str(int(day_print[i]-31)) + '.4', name_print[i]
            if day_print[i]-31 > 30: #Mai
                print '        *', '%6.2f'%DT_print[i], str(int(day_print[i]-31 - 30)) + '.5', name_print[i]
        