import matplotlib.pyplot as plt
import numpy as np
import pandas
import pickle


# get the playtime distribution from a minecraft game trace
def mc_trace():
    # # Code for creating smaller subsets of the data
    # RowID, ServerID, Timestamp, PlayerNum, MaxPlayerNum, UpTime
    # filename = "MineCraft/MineCraft_Node_Server_Fixed_Dynamic"
    # df = pandas.read_csv(filename, skiprows=5, nrows=2000000, dtype={3: str, 4: str})

    # samples = [1000, 100000, 1000000]
    # for s in samples:
    #     df.head(s).to_csv('MineCraft/mc_sample'+str(s)+'.csv', index=False)

    col_names = ["RowID", "ServerID", "Timestamp", "PlayerNum", "MaxPlayerNum", "UpTime"]
    df = pandas.read_csv('MineCraft/mc_sample1000000.csv', skiprows=1, names=col_names, engine="python", \
            dtype={3: str, 4: str}, na_values=[' PlayerNumNull', ' TimestampNull', ' None', ' nan'])
    # df = df[np.isreal(df[["ServerID", "Timestamp", "PlayerNum", "MaxPlayerNum"]])]
    df["Timestamp"] = pandas.to_numeric(df["Timestamp"], errors="coerce")
    df["PlayerNum"] = pandas.to_numeric(df["PlayerNum"], errors="coerce")
    df["MaxPlayerNum"] = pandas.to_numeric(df["MaxPlayerNum"], errors="coerce")
    df = df[pandas.notnull(df["Timestamp"])]
    df = df[pandas.notnull(df["PlayerNum"])]
    df = df[pandas.notnull(df["MaxPlayerNum"])]
    sids = df["ServerID"].unique()
    for sid in sids:
        if sid < 20:
            this_s = df.loc[df["ServerID"] == sid]
            times = list(this_s["Timestamp"])
            n_players = list(this_s["PlayerNum"])
            plt.plot(times, n_players, label=sid)
    plt.xlabel('Time')
    plt.ylabel('Players')
    # plt.legend(loc="best")
    plt.show()


# get the play time distribution from a World of warcraft game trace
def wow_trace():
    # # code for creating smaller subsets of the whole trace
    # filename = "WoWSession/WoWSession_Node_Player_Fixed_Dynamic"
    # df = pandas.read_csv(filename, skiprows=5, sep="\,\ ", nrows=10000000, dtype={3: str, 4: str})

    # samples = [1000, 100000, 1534258]
    # for s in samples:
    #     df.head(s).to_csv('WoWSession/wow_sample'+str(s)+'.csv', index=False)

    col_names = ["RowID", "PlayerID", "Timestamp", "Event", "Category"]
    df = pandas.read_csv('WoWSession/wow_sample1534258.csv', skiprows=1, names=col_names, engine="python", \
            dtype={3: str, 4: str}, na_values=[' PlayerIDNull', ' TimestampNull', ' None', ' nan'])
    # make sure we keep only non null data
    df["Timestamp"] = pandas.to_numeric(df["Timestamp"], errors="coerce")
    df["PlayerNum"] = pandas.to_numeric(df["PlayerID"], errors="coerce")
    df = df[pandas.notnull(df["Timestamp"])]
    df = df[pandas.notnull(df["PlayerID"])]

    # event_types = df["Event"].unique()
    # print(event_types)

    pdf = df.loc[(df["Event"] == "PLAYER_LOGIN") | (df["Event"] == "PLAYER_LOGOUT")]
    playerID = -1
    login_time = -1
    play_times = []
    for _, entry in pdf.iterrows():
        # a player logged in
        if entry["Event"] == "PLAYER_LOGIN":
            # keep track of its id and login time
            playerID = entry["PlayerID"]
            login_time = entry["Timestamp"]
        # a player logged out
        elif entry["PlayerID"] == playerID:
            logout_time = entry["Timestamp"]
            play_time = logout_time - login_time
            # throw away some wrong values (very few (<20))
            if play_time < 60*60*23.5 and play_time > 1:
                play_times.append(play_time)
    print(len(play_times))
    print(np.mean(play_times))
    print(np.std(play_times))
    plt.plot(play_times)
    plt.xlabel('Player')
    plt.ylabel('Time')
    plt.show()

    plt.hist(play_times, 50, [min(play_times),max(play_times)])
    plt.xlabel("Play time")
    plt.ylabel('Number of occurences')
    plt.show()

    return play_times



# got the data printed by the distributor at the end of simulations
# analyze these as a graph
def geo_analysis():
    # 1 server
    data1 = [0.175307643872137, 0.5901095237326712, 0.5282773892568184, 0.8808237110795781, 0.07663158617698057, 0.8043823096015973, 0.8884744003065029, 1.028827614326132, 0.35150170696598326, 0.9724793056924141, 0.5931671349628197, 0.9560381425445326, 0.3247777393849523, 0.4162304289693391, 0.9555143536336855, 0.8077164972934501, 0.9124919999649311, 0.8776510126468265, 0.856839384015464, 0.8323425797110225, 0.8483711039397794, 0.6330535917282201, 0.9551014396387433, 0.7771462217626744, 0.65790310836779, 0.3560643902442366, 0.5871978542195126, 0.33701538540547377, 0.05497090139337353, 0.35819281120647856, 0.22582065893093128, 1.0730497518754665, 0.8712153866868974, 0.2942543967386044, 0.930757379771979, 0.8889309590738754, 0.8535156120423341, 1.0188542780986887, 1.0271250848849909, 0.8740525613485725, 0.283518553184796, 0.9342837738075087, 0.13055213517978168, 0.6364581133114732, 0.8088270643345215, 0.7423535882583179, 0.40348752149230094, 0.4407318572556334, 0.5077025605608071, 0.8101012837911071, 0.34355548314646356, 0.5823563513863311, 0.36261056244957895, 0.7461665497729042, 0.9290802871657541, 0.07363103965040829, 0.2971521159271796, 0.9273907698483956, 0.16426204674239273, 0.7023206390246551, 0.854542275139153, 0.31466650600278384, 0.12201721190061672, 0.4569583460229171, 0.9162111383300248, 0.6762112465790554, 0.5346655777212519, 0.2336768923107289, 0.6635355679991842, 1.0836118308693385, 0.3475934406745904, 0.7836250697878419, 0.10376536030872731, 0.26046314518564806, 0.1244132629585769, 0.8437067085190209, 0.5830201797536686, 0.6240441651037208, 0.9149804642723254, 0.8430875933140043, 0.7968052773419613, 0.9949950401886434, 0.3829592798196696, 0.44876907201811495, 0.6626978874268425, 0.49643393316734497, 0.32964423246888463, 0.9343509030337586, 0.16514251421121093, 0.3940752339338264, 0.37738331971617395, 0.5250102951371525, 0.45585052374654567, 0.2585554099221286, 0.363280236181381, 0.5877109833923474, 0.6792188012709895, 0.912131065143601, 0.14504085631297128, 0.9700333447876934]
    mean1 = 0.6044360382976118
    std1 = 0.2896711235299228
    # 4 servers
    data4 = [0.33593042434408943, 0.21502402191383174, 0.23635136978659546, 0.2716693026456982, 0.15663604310630422, 0.20000142499492346, 0.4697646751300059, 0.40513311392676854, 0.24582125620051654, 0.24618245266468528, 0.07601243319352434, 0.33707945650840254, 0.22830383264413232, 0.2015650019224568, 0.3772304998273602, 0.1781429201512089, 0.29042882088387856, 0.30685374366300305, 0.16702577645381567, 0.2605341628270657, 0.24367790215774598, 0.25822284949244906, 0.20899083711971678, 0.25542045728562934, 0.2239085527620595, 0.34151872569450714, 0.17172868135521213, 0.10450765522199797, 0.2478410175899058, 0.27926698694976465, 0.27101750865949603, 0.483175847906329, 0.2378076533671698, 0.3444439141572979, 0.16490657961403485, 0.25668394963456526, 0.17501228528306234, 0.4654347752370895, 0.3588710353316355, 0.18170288935512283, 0.2956844432837142, 0.04750789408087876, 0.083864772103667, 0.504123605874591, 0.2999277579684815, 0.45144253233385084, 0.23477734132577616, 0.13378613530556893, 0.28265289667717897, 0.28407345880951285, 0.13661332292276623, 0.3658332133636857, 0.2050673304063814, 0.2998282841894674, 0.15951141025017615, 0.18059191565515884, 0.25519563084034175, 0.42490293009109736, 0.09551512969158339, 0.5418225724349255, 0.022012723593413, 0.2525123759343292, 0.18449848237858213, 0.14755761586580343, 0.26623692456156417, 0.17877094282908507, 0.4942606296277299, 0.23236630564692465, 0.1742279254310284, 0.05559901078256698, 0.29969225882561595, 0.21592473225640457, 0.32564354745641744, 0.2636292093073148, 0.2680291402068066, 0.24210311852597027, 0.2733224652310893, 0.37666717404095623, 0.11343249093623926, 0.41317082423617474, 0.11238051432521566, 0.19728114456277873, 0.3220097048226963, 0.3496287459577659, 0.08224463508339008, 0.26187693674701484, 0.35617278110490136, 0.19344066273666458, 0.15383653662248123, 0.2770015523422206, 0.21516765556188971, 0.3651482027889498, 0.13691983055788526, 0.15188459434715557, 0.19923819914865723, 0.21685951673837145, 0.24912426618055497, 0.22155076167776996, 0.2546427497495266, 0.14952073434811639]
    mean4 = 0.2502814103764988
    std4 = 0.10543654214716346
    # 9 servers
    data9 = [0.1014756128338233, 0.14436523127124481, 0.053544000597639314, 0.34466592520874473, 0.17579707051029037, 0.0629880147329633, 0.1531082296938999, 0.1740911255635968, 0.11801377038295155, 0.17204327943863423, 0.20350002457002309, 0.3265149460591353, 0.2627379873562253, 0.04061157470475634, 0.1698738944040549, 0.14496378858183856, 0.15910549959068032, 0.1989599457177247, 0.1703891135020075, 0.1235229938108691, 0.22058912031195008, 0.17311597268883075, 0.06900181157042178, 0.1427403586936785, 0.16678974788637344, 0.22610838109190023, 0.149394812493607, 0.06422086888231901, 0.08603487664894978, 0.10002244748055314, 0.13680953914109936, 0.10229418360786703, 0.09818401091827529, 0.2239647293660321, 0.12569311834782362, 0.08104227291975463, 0.14640491795018362, 0.08817800179183014, 0.16270848164739293, 0.15163772617656865, 0.1823211452355431, 0.1716700323294663, 0.34242365572489286, 0.17051058618162104, 0.08078019559273183, 0.16148027743349963, 0.29997241539848285, 0.16663315996523625, 0.3259795238968239, 0.17615007805845564, 0.20199309394135231, 0.02127204738618265, 0.12325603433503772, 0.16637875465335109, 0.07947332885943564, 0.06876467116186914, 0.260598791248156, 0.16575312968387657, 0.14493850420091967, 0.319445425698976, 0.15364641225879636, 0.20469443079869076, 0.17290488714897562, 0.104940602247176, 0.20289349422788303, 0.15161279629371657, 0.05777793696559267, 0.16142967509104383, 0.014516886718577173, 0.17308824339047407, 0.01889391436415444, 0.1543769736715939, 0.12944883158993747, 0.28784671267881445, 0.15360065104028695, 0.12869052024139152, 0.1919792697142064, 0.312714310513606, 0.09737992606281849, 0.1549859671067029, 0.17845315912025767, 0.13822579354085832, 0.10380525034891054, 0.160263408175416, 0.1038221556316377, 0.20027905532032048, 0.09143680878070934, 0.3144149169489259, 0.34147166793161626, 0.06811438908189665, 0.08421128190450491, 0.17592191449617636, 0.11593467988483859, 0.05236993412254778, 0.13714536084024131, 0.08038438903170193, 0.13290616990945156, 0.0939450903453714, 0.1750009428546029, 0.21347529131025916]
    mean9 = 0.15634006360837108
    std9 = 0.0746026347452319
    #16 servers
    data16 = [0.06553205322588324, 0.14224267995225628, 0.10854943574243023, 0.18614394967336434, 0.1192605550884281, 0.2600682987217012, 0.16302125628273142, 0.15964184914990184, 0.04842003717470692, 0.1092604686059876, 0.1034934297431484, 0.13556430208576298, 0.07248089403422121, 0.1321363689526846, 0.2469183063282267, 0.058826014653382705, 0.11168657036546514, 0.2193053806909443, 0.10804536084441571, 0.03384154251803545, 0.07417526541914092, 0.08818548633420355, 0.028658157651879856, 0.12316967971055216, 0.15274455800453252, 0.10226837243253652, 0.11595537934912724, 0.23605804370959274, 0.09351203131148422, 0.039089896392802116, 0.13860598832662316, 0.12126417442921877, 0.15173888756676715, 0.014681280598094931, 0.07758124773423024, 0.19013092857291788, 0.13207819653523434, 0.11999604160137951, 0.10787993325915621, 0.07381761307438756, 0.1984149187939254, 0.25216443048138254, 0.06635096080690919, 0.2470634129125557, 0.05125085365142711, 0.06918012720427742, 0.11408382882775284, 0.08287321642122986, 0.11458621208504975, 0.11783148984885151, 0.08380214794383259, 0.23110908679669004, 0.08831721236542737, 0.20786813127557577, 0.04404327417438443, 0.1681077035712522, 0.10861017447734814, 0.15758137580310685, 0.10625262349702241, 0.11892627968619893, 0.1785963325491316, 0.11565785749355727, 0.0717508188106589, 0.07738023003325854, 0.12972493977643612, 0.10783955674983095, 0.15437697367159392, 0.10169547679223497, 0.09790812019439449, 0.10373282990451965, 0.23094036026645492, 0.1507042136106353, 0.2467221311516257, 0.07993903927368655, 0.07991107557779463, 0.06825628176219385, 0.11115561164421706, 0.12795518746811319, 0.11036530251849992, 0.1453579375197653, 0.08821813872441425, 0.03482814953453603, 0.19588070349067058, 0.0507445563582933, 0.1219148063198232, 0.11229376652334717, 0.2514108191784912, 0.13960121775973156, 0.11390610168028756, 0.09776630298829957, 0.09257564474525681, 0.0009055385138137523, 0.06972589189103286, 0.04771173859754015, 0.10192472712742477, 0.09575473878613008, 0.13514854790192904, 0.08812746450454591, 0.09308071765945941, 0.08182328519437483]
    mean16 = 0.11897760510719746
    std16 = 0.05704923823291407

    plt.bar([1,4,9,16], [mean1, mean4, mean9, mean16], yerr=[std1, std4, std9, std16])
    plt.xlabel("Number of game servers")
    plt.ylabel('Mean client latency')
    plt.show()



# got the data printed by the populator at the end of simulations
def valid_analysis():
    data = [[0.0,205,1092],
        [0.0,204,1092],
        [0.0,283,1189],
        [0.0,204,1176],
        [0.0,254,866],
        [0.0,201,978],
        [0.0,256,1242],
        [0.0,235,924],
        [0.0,260,826],
        [0.0,223,876],
        [0.1,911,802],
        [0.1,982,885],
        [0.1,829,733],
        [0.1,773,983],
        [0.1,767,888],
        [0.1,942,947],
        [0.1,713,618],
        [0.2,996,731],
        [0.2,861,803],
        [0.2,568,1011],
        [0.2,866,813],
        [0.2,792,956],
        [0.2,975,721],
        [0.2,615,935],
        [0.2,970,776],
        [0.2,880,706],
        [0.4,777,759],
        [0.4,679,875],
        [0.4,652,917],
        [0.4,878,669],
        [0.4,581,946],
        [0.6,687,699],
        [0.6,531,871],
        [0.6,591,732],
        [0.6,604,780],
        [0.6,370,1012],
        [0.6,767,580],
        [0.6,616,757],
        [0.6,488,873],
        [0.6,609,712],
        [0.8,507,423],
        [0.8,588,668],
        [0.8,438,807],
        [0.8,527,674],
        [0.8,528,717],
        [0.8,524,689],
        [0.8,511,679],
        [1,494,688],
        [1,400,765],
        [1,500,640],
        [1,512,653],
        [1,518,666]]

    latencies = [0.0, 0.1, 0.2, 0.4, 0.6, 0.8, 1]
    perc_valid = []
    num_moves = []
    for latency in latencies:
        latency_results = []
        moves_results = []
        for run in data:
            if run[0] == latency:
                percentage = (run[2]/float(run[1]+run[2])) * 100
                latency_results.append(percentage)
                moves = run[1]+run[2]
                moves_results.append(moves)
        perc_valid.append(np.mean(latency_results))
        num_moves.append(np.mean(moves_results))

    plt.plot(latencies, perc_valid)
    plt.xlabel("Latency")
    plt.ylabel("User-friendliness")
    plt.show()

    plt.plot(latencies, num_moves)
    plt.xlabel("Latency")
    plt.ylabel("Number of moves")
    plt.show()


if __name__ == '__main__':
    # mc_trace()
    # play_dist = wow_trace()
    # pickle.dump( play_dist, open( "wow_trace.p", "wb" ) )
    # geo_analysis()
    valid_analysis()