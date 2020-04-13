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
                           usecols=(9,2,8,5,6,-1),
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
        case_state.append(np.sum(case_state_dat[case_state_dat > 0]))
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
        li = dat_sting[i].split('-')
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
        ufall[i] = np.sum(fall_day[fall_day > 0])
        
        tod_day = RKI_tab['tod'][cond]
        utod[i] = np.sum(tod_day[tod_day > 0])
        #print tod_day[tod_day < 0]
        
        gesund_day = RKI_tab['gesund'][cond]
        ugesund[i] = np.sum(gesund_day[gesund_day > 0])
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
    '''
    import matplotlib.pyplot as plt
    import numpy as np
    from scipy.optimize import curve_fit
    
    print '-' * 30
    print name
    print '-' * 30
    
    num = num_dic['fall']
    num_tod = num_dic['tod']
    num_gesund = num_dic['gesund']
    
    fig, ax = plt.subplots(figsize=(10,8))
    plt.title(name + ' (#' + ID +')')
    ax.axis([13, 50, 0.9, 1e5])
    
    ####
    # move to March time frame
    #########
    day_real = np.copy(day)
    day[month == 2] = day[month == 2] - 29
    day[month == 1] = day[month == 1] - 29 - 31
    day[month == 4] = day[month == 4] + 31
    
    #########
    # fit
    #########
    def func(x, a, b):#, c):
        #return a * np.exp(b * x)# + c #
        #return a * b**(c*x)
        return np.log(a) + b * x  #log-linear
    
    x = np.arange(10,50,0.5)
    
    # fit only when there are more than 6 data points and cases every day.
    data_points = range(8, len(day)+1)
    
    DTs = []
    Ntot_today = []
    Ntot_week = []
    
    col = 30
    colapp = []
    print 'Tag  DTs'
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
        
        #########
        # doubling time
        #########
        DT = np.round(np.log(2) / popt[1],2)
        #print DT#,  popt
        DTs.append(DT)
        #print popt, np.log(2) / popt[1]

        print '%02d'%int(day_real[cut-1]) + '.' +  '%02d'%int(month[cut-1]), '%5.2f'%DT

        #print("a =", popt[0], "+/-", pcov[0,0]**0.5)
        #print("b =", popt[1], "+/-", pcov[1,1]**0.5)
        #print("c =", popt[2], "+/-", pcov[2,2]**0.5)
    
        ##########
        # plot
        ##########
        
        
        ########
        # plot fit
        #########
        day_label = 'Fit am ' + '%02d'%int(day_real[cut-1]) + '.' + '%02d'%int(month[cut-1]) + '; VZ: ' + '%5.2f'%DT + ' d'
        plt.semilogy(x, np.exp(func(x, *popt)), '-', color=plt.cm.viridis(int(col)), 
                     label=day_label)
        
        colapp.append(int(col))
        col = col + 256 / len(data_points)         

        ########
        # plot Beatmungsbedarf        
        #########
        if cut == data_points[-1]:
            
            # Beatmungsampel
            bedarf =  anteil_beatmung * np.exp(func(x, *popt))
            
            plt.semilogy(x, bedarf, 
                         '-', lw=3, color=plt.cm.Reds(200), 
                         label='Ampel (Beatmungsbedarf ca. ' + str(int(anteil_beatmung*100)) + '%)')
            plt.semilogy(x[(bedarf < geraet_max)],bedarf[(bedarf < geraet_max)], 
                         '-', lw=3, color=plt.cm.jet(180), 
                         label='Ampel (Beatmungsbedarf ca. ' + str(int(anteil_beatmung*100)) + '%)')
            plt.semilogy(x[bedarf < geraet_min],bedarf[bedarf < geraet_min], 
                         '-', lw=3, color=plt.cm.Greens(200), 
                         label='Ampel (Beatmungsbedarf ca. ' + str(int(anteil_beatmung*100)) + '%)')
            
            # Fehler
            plt.semilogy(x, 0.05*np.exp(func(x, 
                                 popt[0] - pcov[0,0]**0.5, 
                                 popt[1] - pcov[1,1]**0.5)), 
                                 #popt[2] - pcov[2,2]**0.5), 
                         '--', color='k', alpha=0.5, label='Unsicherheiten')
            plt.semilogy(x, 0.05*np.exp(func(x, 
                                 popt[0] + pcov[0,0]**0.5, 
                                 popt[1] + pcov[1,1]**0.5)), 
                                 #popt[2] + pcov[2,2]**0.5), 
                         '--', color='k', alpha=0.5)
    
    
    
    ####
    # Beatmungs Kapazitaet
    #########
    plt.plot([x[0], x[-1]], [geraet_min]*2, 'k:', label="Kapazitaet Beatmungsapparate")
    plt.plot([x[0], x[-1]], [geraet_max]*2, 'k:')
    
    ####
    # gemeldete Fallzahlen
    #########
    plt.semilogy(day, num, 'k+', label="COVID19 erkrankt")
    plt.semilogy(day, num_tod, 'k*', label="davon verstorben")
    plt.semilogy(day, num_gesund, 'ko', alpha=0.3, label="davon genesen")
    
    print '+' * 30
    print 'Sterberate (%): ', np.round(num_tod[-1] / num[-1] * 100, 2)
    print 'Gesunde (%):    ', np.round(num_gesund[-1] / num[-1] * 100, 2)
    print '+' * 30
    
    
    
    #############
    # formating
    #############
    
    from matplotlib.ticker import ScalarFormatter
    for axis in [ax.xaxis, ax.yaxis]:
        axis.set_major_formatter(ScalarFormatter())
    ax.grid(True, which="both")
    plt.xticks(np.arange(14, 50, 2))
    ax.set_xticklabels([14, 16, 18, 20, 22, 24, 26, 28, 30, 1, 3, 5, 7, 9, 11, 13, 15, 17])
    
    tx1 = ax.text(13, 0.5, 'Maerz')
    tx2 = ax.text(31, 0.5, 'April')
    
    ax.text(54.5, 9e4, 'Christine Greif', fontsize=8)
    link = ax.text(54.5, 7.4e4, 'http://www.usm.uni-muenchen.de/~koepferl', fontsize=8)
    ax.text(54.5, 5.9e4, 'This work is licensed under CC-BY-SA 4.0', fontsize=8)
    ax.text(54.5, 4.6e4, 'Data: NPGEO-DE; VZ = Verdopplungszeit ', fontsize=8)
    link.set_url('http://www.usm.uni-muenchen.de/~koepferl')
    ax.set_ylabel('Fallzahlen')
    lgd = ax.legend(loc='best', bbox_to_anchor=(1.12, 0.93))
    
    # percent
    #########
    EW_county = get_people_of_county(asked_ID=ID)
    
    axi = ax.twinx()
    
    #print 'lim', ax.get_ylim(), ax.get_ylim()[0] / EW_county * 100, ax.get_ylim()[1] / EW_county * 100, EW_county
    axi.set_ylim(ax.get_ylim()[0] / EW_county * 100 , ax.get_ylim()[1] / EW_county * 100 )
    axi.set_yscale('log')
    import matplotlib.ticker as mtick
    import matplotlib.ticker as ticker
    axi.yaxis.set_major_formatter(ScalarFormatter())
    axi.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y,pos: ('{{:.{:1d}f}}%'.format(int(np.maximum(-np.log10(y),0)))).format(y)))
    #axi.yaxis.set_major_formatter(FormatStrFormatter('%4d'))
    #axi.yaxis.set_major_formatter(mtick.PercentFormatter())
    axi.set_ylabel('Prozentualer Anteil zur Gesamteinwohnerzahl (' + str(EW_county) + ') im Kreis')
    
    fig.savefig('plots/' + name + '.pdf', dpi=300, overwrite=True, 
                bbox_extra_artists=(lgd, tx1, tx2,), bbox_inches='tight')
                
    #raise Exception('stop')
    
    
    
    return [name, day[7:], DTs, Ntot_today, Ntot_week]

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
    
    dat_states = state[1]
    
    state_day = []
    for i in range(len(dat_states)):
        y, m, d = dat_states[i].split('-')
        if m == '01': state_day.append(int(d) - 29 - 31)
        if m == '02': state_day.append(int(d) - 29)
        if m == '03': state_day.append(int(d))
        if m == '04': state_day.append(int(d) + 31) 
    
    #########
    # fit
    #########
    def func(x, a, b):#, c):
        #return a * np.exp(b * x)# + c
        #return a * b**(c*x)
        return np.log(a) + b * x
    
    x = np.arange(10,50,0.5)
    
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
            line_col = 20 + 30 * (8 - i)

        if i in range(8, 16): 
            ax = axs[0,1]
            ax2 = axs2[0,1]
            line_col = 20 + 30 * (16 - i)

        if i in range(16,24): 
            ax = axs[0,2]
            ax2 = axs2[0,2]
            line_col = 20 + 30 * (24 - i)

        if i in range(24,32): 
            ax = axs[0,3]
            ax2 = axs2[0,3]
            line_col = 20 + 30 * (32 - i)

        if i in range(32,40): 
            ax = axs[1,0]
            ax2 = axs2[1,0]
            line_col = 20 + 30 * (40 - i)

        if i in range(40,48): 
            ax = axs[1,1]
            ax2 = axs2[1,1]
            line_col = 20 + 30 * (48 - i)

        if i in range(48,56): 
            ax = axs[1,2]
            ax2 = axs2[1,2]
            line_col = 20 + 30 * (56 - i)

        if i in range(56,64): 
            ax = axs[1,3]
            ax2 = axs2[1,3]
            line_col = 20 + 30 * (64 - i)

        if i in range(64,72): 
            ax = axs[2,0]
            ax2 = axs2[2,0]
            line_col = 20 + 30 * (72 - i)

        if i in range(72,80): 
            ax = axs[2,1]
            ax2 = axs2[2,1]
            line_col = 20 + 30 * (80 - i)

        if i in range(80,88): 
            ax = axs[2,2]
            ax2 = axs2[2,2]
            line_col = 20 + 30 * (88 - i)

        if i in range(88,96): 
            ax = axs[2,3]
            ax2 = axs2[2,3]
            line_col = 20 + 30 * (96 - i)
            
        key = sorted_keys[i]
        if i in [0, 8 ,16, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96]:
            ax.plot(state_day[7:], DTs_state, '.:k', label= state[2] + ' average')
            print '-' * 20
            print state[2], DTs_state[-1], int(state_day[7:][-1])
            print '-' * 20
        
        ax.plot(DT[key][1], DT[key][2], '.-', c = cmap(line_col), label=DT[key][0])
        ax2.loglog(DT[key][3], DT[key][4], '.-', c = cmap(line_col), label=DT[key][0])
        print DT[key][2][-1], int(DT[key][1][-1]), DT[key][0]
        
    
    ######
    # axis
    
    link = axs[2,3].text(27, -3.6, 'Christine Greif (http://www.usm.uni-muenchen.de/~koepferl)', fontsize=8)
    axs[2,3].text(27, -4.6, 'This work is licensed under CC-BY-SA 4.0', fontsize=8)
    axs[2,3].text(27, -5.6, 'Data: NPGEO-DE', fontsize=8)
    
    link = axs2[2,3].text(35, 5, 'Christine Greif (http://www.usm.uni-muenchen.de/~koepferl)', fontsize=8)
    axs2[2,3].text(35, 4.4, 'This work is licensed under CC-BY-SA 4.0', fontsize=8)
    axs2[2,3].text(35, 3.8, 'Data: NPGEO-DE', fontsize=8)
    
    link.set_url('http://www.usm.uni-muenchen.de/~koepferl')

    
    axs[0,0].set_ylabel('Verdopplungszeiten (Tage)')
    axs[1,0].set_ylabel('Doubling Time DT (days)')
    axs[2,0].set_ylabel('Verdopplungszeiten (Tage)')

    
    for ax in axs.reshape(-1):
        ax.set_ylim(0,30.9)
        ax.set_xlim(13,50)
    
        ax.grid(True, which="both")
        ax.set_xticks(np.arange(14, 50, 2))
        ax.set_xticklabels([14, 16, 18, 20, 22, 24, 26, 28, 30, 1, 3, 5, 7, 9, 11, 13, 15, 17])
    
        ax.legend(loc='upper left')
    
        #if ax in [axs[2,0], axs[2,1], axs[2,2], axs[2,3]]:
        ax.text(13, -2.5, 'Maerz/March')
        ax.text(31, -2.5, 'April')
    
            
    for ax2 in axs2.reshape(-1):
        
        from matplotlib.ticker import ScalarFormatter
        for axis in [ax2.xaxis, ax2.yaxis]:
            axis.set_major_formatter(ScalarFormatter())
        ax2.grid(True, which="both")
        
        ax2.set_ylim(10.5,2000)
        ax2.set_xlim(10.5,10000)
        ax2.legend(loc='upper left')
        
        if ax2 in [axs2[2,0], axs2[2,1], axs2[2,2], axs2[2,3]]:
            ax2.set_xlabel('Totale Fallzahlen (total number of cases)')
        if ax2 in [axs2[0,0], axs2[1,0], axs2[2,0]]:
            ax2.set_ylabel('Fallzahlen in der letzten Woche (number of new cases last week)')
        
        
    
    
    #plt.show()
    fig.savefig('DT_' + state[2] + '.pdf', dpi=300, overwrite=True, bbox_inches='tight')
    fig2.savefig('loglog_' + state[2] + '.pdf', dpi=300, overwrite=True, bbox_inches='tight')
    
    #################
    #plt.title(name)
    
    for i in range(len(sorted_keys)):
        plt.loglog()
    
    