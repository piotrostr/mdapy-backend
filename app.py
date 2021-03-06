import sys
import json

from mdapy import load_data, validate_analyses_df
from MDAPy import MDAPy_Functions as mdapy
from flask import Flask, jsonify, request, make_response


app = Flask(__name__)

def parse_params(data):
    if data['dataset'] == 'Best Age and sx':
        Data_Type = 'Ages'
    elif data['dataset'] == 'U-Pb 238/206 & Pb-Pb 207/206':
        Data_Type = '238U/206Pb_&_207Pb/206Pb'
    sample_list = data['samplesToPlot']
    if 'All Samples' in sample_list:
        main_df, *_ = parse_dfs(data)
        sample_list = main_df['Sample_ID'].tolist()
    if data['sigma'] == '1 sx':
        sigma = 1
    elif data['sigma'] == '2 sx':
        sigma = 2
    if data['uncertaintyFormat'] == 'Percent %':
        uncertainty = 'percent'
    else:
        uncertainty = 'absolute'
    # the below assumes that the user will not input text instead of numbers for 
    # both the decay constants
    best_age_cut_off = int(data['bestAgeCutOff'])
    U238_decay_constant = eval(data['primaryDecayConstant'])
    U235_decay_constant = eval(data['secondaryDecayConstant'])
    U238_U235 = float(data['thirdDecayConstant'])
    excess_variance_206_238 = float(data['primaryLongTermVar'])
    excess_variance_207_206 = float(data['secondaryLongTermVar'])
    Sy_calibration_uncertainty_206_238 = float(data['primaryCalibrationUncertainty'])
    Sy_calibration_uncertainty_207_206 = float(data['secondaryCalibrationUncertainty'])
    decay_constant_uncertainty_U238 = float(data['primaryDecayUncertainty'])
    decay_constant_uncertainty_U235 = float(data['secondaryDecayUncertainty'])
    return ( 
        Data_Type, sample_list, sigma, uncertainty, best_age_cut_off, 
        U238_decay_constant, U235_decay_constant, U238_U235,
        excess_variance_206_238, excess_variance_207_206, 
        Sy_calibration_uncertainty_206_238, Sy_calibration_uncertainty_207_206, 
        decay_constant_uncertainty_U238, decay_constant_uncertainty_U235
    )


def parse_float(x):
    try:
        if ',' in x:
            return float(x.replace(',', '.'))
        return float(x)
    except:
        return x


def parse_dfs(data):
    """
    :returns tuple: main_df, main_byid_df, samples_df, analyses_df 
    """
    arrays = data['table']['data']
    arrays = [[i['value'] for i in row] for row in arrays]
    arrays = [list(map(parse_float, array)) for array in arrays]
    column_names = data['table']['columnLabels']
    dataset = data['dataset']
    if dataset == 'Best Age and sx':
        data_type = 'Ages'
    elif dataset == 'U-Pb 238/206 & Pb-Pb 207/206':
        data_type = '238U/206Pb_&_207Pb/206Pb'
    return load_data(arrays, column_names, data_type)


def sign(response):
    methods_allowed = 'GET,HEAD,OPTIONS,POST,PUT'
    headers_allowed = 'Access-Control-Allow-Headers, Origin, Accept, ' 
    headers_allowed += 'X-Requested-With, Content-Type, ' 
    headers_allowed += 'Access-Control-Request-Method, ' 
    headers_allowed += 'Access-Control-Request-Headers'
    response.headers['Access-Control-Allow-Origin'] = '*' 
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = methods_allowed
    response.headers['Access-Control-Allow-Headers'] = headers_allowed
    response.headers['Content-Type'] = 'application/json'
    return response 


@app.route('/')
def index():
    return jsonify('MDAPy API home')


# LOAD DATA

@app.route('/validate', methods=['POST', 'OPTIONS'])
def check_validity():
    if not len(request.data):
        msg = 'no data could be retrieved from your request'
        response = make_response(jsonify(msg))
        return sign(response)
    data = json.loads(request.data)
    dataset = data['dataset']
    if dataset == 'Best Age and sx':
        data_type = 'Ages'
    elif dataset == 'U-Pb 238/206 & Pb-Pb 207/206':
        data_type = '238U/206Pb_&_207Pb/206Pb'
    *_, analyses_df = parse_dfs(data)
    sample_amounts_table = validate_analyses_df(analyses_df, data_type)
    response = make_response(sample_amounts_table.to_json())
    return sign(response)


# CALCULATE ALL MDA METHODS AND PLOT

@app.route('/calculate_all_mda_methods', methods=['POST', 'OPTIONS'])
def calculate_all_mda_methods():
    if not len(request.data):
        msg = 'no data could be retrieved from your request'
        response = make_response(jsonify(msg))
        return sign(response)
    data = json.loads(request.data)
    main_df, main_byid_df, samples_df, analyses_df = parse_dfs(data)
    (
        Data_Type, sample_list, sigma, uncertainty, best_age_cut_off, 
        U238_decay_constant, U235_decay_constant, U238_U235, 
        excess_variance_206_238, excess_variance_207_206, 
        Sy_calibration_uncertainty_206_238, Sy_calibration_uncertainty_207_206, 
        decay_constant_uncertainty_U238, decay_constant_uncertainty_U235
    ) = parse_params(data)
    ( 
	ages, errors, eight_six_ratios, eight_six_error,
        seven_six_ratios, seven_six_error, numGrains, labels,
	sample_list, best_age_cut_off, dataToLoad_MLA,
	U238_decay_constant,U235_decay_constant,U238_U235,
	excess_variance_206_238, excess_variance_207_206, 
	Sy_calibration_uncertainty_206_238, 
	Sy_calibration_uncertainty_207_206, 
	decay_constant_uncertainty_U238,
	decay_constant_uncertainty_U235
    ) = mdapy.sampleToData(
	sample_list,
	main_byid_df, 
	sigma,
	Data_Type,
	uncertainty,
        best_age_cut_off,
	U238_decay_constant,
	U235_decay_constant,
	U238_U235,excess_variance_206_238,
	excess_variance_207_206,
	Sy_calibration_uncertainty_206_238,
	Sy_calibration_uncertainty_207_206,
	decay_constant_uncertainty_U238, 
	decay_constant_uncertainty_U235
    )
    dataToLoad_MLA = ['Data/_.xlsx']  # bypass the excel save-requiring bug
    (
	U238_decay_constant, U235_decay_constant, U238_U235, YSG_MDA,
	YC1s_MDA, YC1s_cluster_arrays, YC2s_MDA, YC2s_cluster_arrays,
	YDZ_MDA, minAges, mode, Y3Zo_MDA, Y3Zo_cluster_arrays, Y3Za_MDA,
	Y3Za_cluster_arrays, Tau_MDA, Tau_Grains, PDP_age, PDP,plot_max,
	ages_errors1s_filtered, tauMethod_WM, tauMethod_WM_err2s, 
	YSP_MDA, YSP_cluster, YPP_MDA, MLA_MDA
    ) = mdapy.MDA_Calculator(
	ages, errors, sample_list, dataToLoad_MLA, eight_six_ratios, 
	eight_six_error, seven_six_ratios, seven_six_error, U238_decay_constant,
	U235_decay_constant,U238_U235, excess_variance_206_238, 
	excess_variance_207_206, Sy_calibration_uncertainty_206_238, 
	Sy_calibration_uncertainty_207_206, decay_constant_uncertainty_U238,
	decay_constant_uncertainty_U235, Data_Type, best_age_cut_off
    )

    MDAs_1s_table, excel_MDA_data, all_MDA_data = mdapy.output_tables(
        sample_list, YSG_MDA, YC1s_MDA, YC2s_MDA, YDZ_MDA, Y3Zo_MDA,
        Y3Za_MDA, Tau_MDA, YSP_MDA, YPP_MDA, MLA_MDA
    )

    plotwidth = 10
    plotheight = 7
    Image_File_Option = 'svg'

    mdapy.Plot_MDA(
        MDAs_1s_table, all_MDA_data, sample_list, YSG_MDA, YC1s_MDA, 
        YC2s_MDA, YDZ_MDA, Y3Zo_MDA, Y3Za_MDA, Tau_MDA, YSP_MDA, YPP_MDA, 
        MLA_MDA, Image_File_Option, plotwidth, plotheight
    )

    fname = 'Saved_Files/All_MDA_Methods_Plots/All_MDA_Methods_Plots.svg'
    with open(fname, 'r') as f:
        svg = f.read()
    response = make_response(json.dumps(
            [MDAs_1s_table.to_json(), json.dumps(svg)]
        )
    )
    return sign(response)


# CALCULATE INDIVIDUAL MDAS AND PLOT

@app.route('/calculate_individual_YC1s', methods=['POST', 'OPTIONS'])
def calculate_individual_YC1s():
    if not len(request.data):
        msg = 'no data could be retrieved from your request'
        response = make_response(jsonify(msg))
        return sign(response)
    data = json.loads(request.data)
    main_df, main_byid_df, samples_df, analyses_df = parse_dfs(data)
    (
        Data_Type, sample_list, sigma, uncertainty, best_age_cut_off, 
        U238_decay_constant, U235_decay_constant, U238_U235, 
        excess_variance_206_238, excess_variance_207_206, 
        Sy_calibration_uncertainty_206_238, Sy_calibration_uncertainty_207_206, 
        decay_constant_uncertainty_U238, decay_constant_uncertainty_U235
    ) = parse_params(data)
    ( 
	ages, errors, eight_six_ratios, eight_six_error,
        seven_six_ratios, seven_six_error, numGrains, labels,
	sample_list, best_age_cut_off, dataToLoad_MLA,
	U238_decay_constant,U235_decay_constant,U238_U235,
	excess_variance_206_238, excess_variance_207_206, 
	Sy_calibration_uncertainty_206_238, 
	Sy_calibration_uncertainty_207_206, 
	decay_constant_uncertainty_U238,
	decay_constant_uncertainty_U235
    ) = mdapy.sampleToData(
	sample_list,
	main_byid_df, 
	sigma,
	Data_Type,
	uncertainty,
        best_age_cut_off,
	U238_decay_constant,
	U235_decay_constant,
	U238_U235,excess_variance_206_238,
	excess_variance_207_206,
	Sy_calibration_uncertainty_206_238,
	Sy_calibration_uncertainty_207_206,
	decay_constant_uncertainty_U238, 
	decay_constant_uncertainty_U235
    )

    YC1s_MDA, YC1s_cluster_arrays = mdapy.YC1s(
        ages, errors, sample_list,
        eight_six_ratios, eight_six_error, seven_six_ratios,
        seven_six_error, U238_decay_constant, U235_decay_constant,
        U238_U235, excess_variance_206_238, excess_variance_207_206,
        Sy_calibration_uncertainty_206_238,
        Sy_calibration_uncertainty_207_206,
        decay_constant_uncertainty_U238,
        decay_constant_uncertainty_U235, Data_Type, best_age_cut_off,
        min_cluster_size=2
    )

    plotwidth = 10
    plotheight = 7
    age_addition_set_max_plot = 30
    Image_File_Option = 'svg'

    _, table = mdapy.YC1s_outputs(
        ages,
        errors,
        sample_list,
        YC1s_MDA,
        YC1s_cluster_arrays,
        plotwidth,
        plotheight,
        age_addition_set_max_plot,
        Image_File_Option,
        min_cluster_size=2,
    )

    fname = 'Saved_Files/Individual_MDA_Plots/YC1s_Plots.svg'
    with open(fname, 'r') as f:
        svg = f.read()
    response = make_response(json.dumps(
            [table.to_json(), json.dumps(svg)]
        )
    )
    return sign(response)


@app.route('/calculate_individual_YC2s', methods=['POST', 'OPTIONS'])
def calculate_individual_YC2s():
    if not len(request.data):
        msg = 'no data could be retrieved from your request'
        response = make_response(jsonify(msg))
        return sign(response)
    data = json.loads(request.data)
    main_df, main_byid_df, samples_df, analyses_df = parse_dfs(data)
    (
        Data_Type, sample_list, sigma, uncertainty, best_age_cut_off, 
        U238_decay_constant, U235_decay_constant, U238_U235, 
        excess_variance_206_238, excess_variance_207_206, 
        Sy_calibration_uncertainty_206_238, Sy_calibration_uncertainty_207_206, 
        decay_constant_uncertainty_U238, decay_constant_uncertainty_U235
    ) = parse_params(data)
    ( 
	ages, errors, eight_six_ratios, eight_six_error,
        seven_six_ratios, seven_six_error, numGrains, labels,
	sample_list, best_age_cut_off, dataToLoad_MLA,
	U238_decay_constant,U235_decay_constant,U238_U235,
	excess_variance_206_238, excess_variance_207_206, 
	Sy_calibration_uncertainty_206_238, 
	Sy_calibration_uncertainty_207_206, 
	decay_constant_uncertainty_U238,
	decay_constant_uncertainty_U235
    ) = mdapy.sampleToData(
	sample_list,
	main_byid_df, 
	sigma,
	Data_Type,
	uncertainty,
        best_age_cut_off,
	U238_decay_constant,
	U235_decay_constant,
	U238_U235,excess_variance_206_238,
	excess_variance_207_206,
	Sy_calibration_uncertainty_206_238,
	Sy_calibration_uncertainty_207_206,
	decay_constant_uncertainty_U238, 
	decay_constant_uncertainty_U235
    )

    YC2s_MDA, YC2s_cluster_arrays = mdapy.YC2s(
        ages, errors, sample_list,
        eight_six_ratios, eight_six_error, seven_six_ratios,
        seven_six_error, U238_decay_constant, U235_decay_constant,
        U238_U235, excess_variance_206_238, excess_variance_207_206,
        Sy_calibration_uncertainty_206_238,
        Sy_calibration_uncertainty_207_206,
        decay_constant_uncertainty_U238,
        decay_constant_uncertainty_U235, Data_Type, best_age_cut_off,
        min_cluster_size=2
    )

    plotwidth = 10
    plotheight = 7
    age_addition_set_max_plot = 30
    Image_File_Option = 'svg'

    _, table = mdapy.YC2s_outputs(
        ages,
        errors,
        sample_list,
        YC2s_MDA,
        YC2s_cluster_arrays,
        plotwidth,
        plotheight,
        age_addition_set_max_plot,
        Image_File_Option,
        min_cluster_size=2,
    )

    fname = 'Saved_Files/Individual_MDA_Plots/YC2s_Plots.svg'
    with open(fname, 'r') as f:
        svg = f.read()
    response = make_response(json.dumps(
            [table.to_json(), json.dumps(svg)]
        )
    )
    return sign(response)


@app.route('/calculate_individual_YSG', methods=['POST', 'OPTIONS'])
def calculate_individual_YSG():
    if not len(request.data):
        msg = 'no data could be retrieved from your request'
        response = make_response(jsonify(msg))
        return sign(response)
    data = json.loads(request.data)
    main_df, main_byid_df, samples_df, analyses_df = parse_dfs(data)
    (
        Data_Type, sample_list, sigma, uncertainty, best_age_cut_off, 
        U238_decay_constant, U235_decay_constant, U238_U235, 
        excess_variance_206_238, excess_variance_207_206, 
        Sy_calibration_uncertainty_206_238, 
        Sy_calibration_uncertainty_207_206, 
        decay_constant_uncertainty_U238, decay_constant_uncertainty_U235
    ) = parse_params(data)
    ( 
	ages, errors, eight_six_ratios, eight_six_error,
        seven_six_ratios, seven_six_error, numGrains, labels,
	sample_list, best_age_cut_off, dataToLoad_MLA,
	U238_decay_constant,U235_decay_constant,U238_U235,
	excess_variance_206_238, excess_variance_207_206, 
	Sy_calibration_uncertainty_206_238, 
	Sy_calibration_uncertainty_207_206, 
	decay_constant_uncertainty_U238,
	decay_constant_uncertainty_U235
    ) = mdapy.sampleToData(
	sample_list,
	main_byid_df, 
	sigma,
	Data_Type,
	uncertainty,
        best_age_cut_off,
	U238_decay_constant,
	U235_decay_constant,
	U238_U235,excess_variance_206_238,
	excess_variance_207_206,
	Sy_calibration_uncertainty_206_238,
	Sy_calibration_uncertainty_207_206,
	decay_constant_uncertainty_U238, 
	decay_constant_uncertainty_U235
    )

    YSG_MDA = mdapy.YSG(
        ages, errors, sample_list, excess_variance_206_238,
        excess_variance_207_206,
        Sy_calibration_uncertainty_206_238,
        Sy_calibration_uncertainty_207_206,
        decay_constant_uncertainty_U238,
        decay_constant_uncertainty_U235, Data_Type,
        best_age_cut_off
    )

    plotwidth = 10
    plotheight = 7
    age_addition_set_max_plot = 30
    Image_File_Option = 'svg'

    _, table = mdapy.YSG_outputs(
        ages, errors, plotwidth, plotheight,
        sample_list, YSG_MDA, age_addition_set_max_plot,
        Image_File_Option
    )

    fname = 'Saved_Files/Individual_MDA_Plots/YSG_Plots.svg'
    with open(fname, 'r') as f:
        svg = f.read()
    response = make_response(json.dumps(
            [table.to_json(), json.dumps(svg)]
        )
    )
    return sign(response)


@app.route('/calculate_individual_Tau', methods=['POST', 'OPTIONS'])
def calculate_individual_Tau():
    if not len(request.data):
        msg = 'no data could be retrieved from your request'
        response = make_response(jsonify(msg))
        return sign(response)
    data = json.loads(request.data)
    main_df, main_byid_df, samples_df, analyses_df = parse_dfs(data)
    (
        Data_Type, sample_list, sigma, uncertainty, best_age_cut_off, 
        U238_decay_constant, U235_decay_constant, U238_U235, 
        excess_variance_206_238, excess_variance_207_206, 
        Sy_calibration_uncertainty_206_238, 
        Sy_calibration_uncertainty_207_206, 
        decay_constant_uncertainty_U238, 
        decay_constant_uncertainty_U235
    ) = parse_params(data)
    ( 
	ages, errors, eight_six_ratios, eight_six_error,
        seven_six_ratios, seven_six_error, numGrains, labels,
	sample_list, best_age_cut_off, dataToLoad_MLA,
	U238_decay_constant,U235_decay_constant,U238_U235,
	excess_variance_206_238, excess_variance_207_206, 
	Sy_calibration_uncertainty_206_238, 
	Sy_calibration_uncertainty_207_206, 
	decay_constant_uncertainty_U238,
	decay_constant_uncertainty_U235
    ) = mdapy.sampleToData(
	sample_list,
	main_byid_df, 
	sigma,
	Data_Type,
	uncertainty,
        best_age_cut_off,
	U238_decay_constant,
	U235_decay_constant,
	U238_U235,excess_variance_206_238,
	excess_variance_207_206,
	Sy_calibration_uncertainty_206_238,
	Sy_calibration_uncertainty_207_206,
	decay_constant_uncertainty_U238, 
	decay_constant_uncertainty_U235
    )

    (
        Tau_MDA, Tau_Grains, PDP_age, PDP, plot_max, 
        ages_errors1s_filtered, tauMethod_WM, tauMethod_WM_err2s
    )= mdapy.tau(
        ages, errors, sample_list,
        eight_six_ratios, eight_six_error, seven_six_ratios,
        seven_six_error, U238_decay_constant, U235_decay_constant,
        U238_U235, excess_variance_206_238, excess_variance_207_206,
        Sy_calibration_uncertainty_206_238,
        Sy_calibration_uncertainty_207_206,
        decay_constant_uncertainty_U238, 
        decay_constant_uncertainty_U235, Data_Type, best_age_cut_off, 
        min_cluster_size=3, thres=0.01, minDist=1, xdif=1, x1=0, x2=4000
    )

    plotwidth = 10
    plotheight = 7
    age_addition_set_max_plot = 30
    Image_File_Option = 'svg'

    _, table = mdapy.Tau_outputs(
        ages, errors, sample_list, eight_six_ratios,
        eight_six_error, seven_six_ratios, seven_six_error,
        U238_decay_constant, U235_decay_constant, U238_U235, Data_Type,
        best_age_cut_off, plotwidth, plotheight, Image_File_Option,
        min_cluster_size=3, thres=0.01, minDist=1, xdif=1, x1=0, x2=4000
    )

    fname = 'Saved_Files/Individual_MDA_Plots/Tau_Plots.svg'
    with open(fname, 'r') as f:
        svg = f.read()
    response = make_response(json.dumps(
            [table.to_json(), json.dumps(svg)]
        )
    )
    return sign(response)


@app.route('/calculate_individual_YSP', methods=['POST', 'OPTIONS'])
def calculate_individual_YSP():
    if not len(request.data):
        msg = 'no data could be retrieved from your request'
        response = make_response(jsonify(msg))
        return sign(response)
    data = json.loads(request.data)
    main_df, main_byid_df, samples_df, analyses_df = parse_dfs(data)
    (
        Data_Type, sample_list, sigma, uncertainty, best_age_cut_off, 
        U238_decay_constant, U235_decay_constant, U238_U235, 
        excess_variance_206_238, excess_variance_207_206, 
        Sy_calibration_uncertainty_206_238, 
        Sy_calibration_uncertainty_207_206, 
        decay_constant_uncertainty_U238, decay_constant_uncertainty_U235
    ) = parse_params(data)
    ( 
	ages, errors, eight_six_ratios, eight_six_error,
        seven_six_ratios, seven_six_error, numGrains, labels,
	sample_list, best_age_cut_off, dataToLoad_MLA,
	U238_decay_constant,U235_decay_constant,U238_U235,
	excess_variance_206_238, excess_variance_207_206, 
	Sy_calibration_uncertainty_206_238, 
	Sy_calibration_uncertainty_207_206, 
	decay_constant_uncertainty_U238,
	decay_constant_uncertainty_U235
    ) = mdapy.sampleToData(
	sample_list,
	main_byid_df, 
	sigma,
	Data_Type,
	uncertainty,
        best_age_cut_off,
	U238_decay_constant,
	U235_decay_constant,
	U238_U235,excess_variance_206_238,
	excess_variance_207_206,
	Sy_calibration_uncertainty_206_238,
	Sy_calibration_uncertainty_207_206,
	decay_constant_uncertainty_U238, 
	decay_constant_uncertainty_U235
    )

    YSP_MDA, YSP_cluster = mdapy.YSP(
        ages, errors, sample_list, eight_six_ratios,
        eight_six_error, seven_six_ratios, seven_six_error,
        U238_decay_constant, U235_decay_constant, U238_U235,
        excess_variance_206_238, excess_variance_207_206,
        Sy_calibration_uncertainty_206_238,
        Sy_calibration_uncertainty_207_206,
        decay_constant_uncertainty_U238, 
        decay_constant_uncertainty_U235,
        Data_Type, best_age_cut_off, 
        min_cluster_size=2, MSWD_threshold=1
    )

    plotwidth = 10
    plotheight = 7
    age_addition_set_max_plot = 30
    Image_File_Option = 'svg'

    _, table = mdapy.YSP_outputs(
        ages, errors, sample_list, YSP_MDA,
        YSP_cluster, plotwidth, plotheight, 
        age_addition_set_max_plot,
        Image_File_Option, 
        min_cluster_size=2, MSWD_threshold=1
    )

    fname = 'Saved_Files/Individual_MDA_Plots/YSP_Plots.svg'
    with open(fname, 'r') as f:
        svg = f.read()
    response = make_response(json.dumps(
            [table.to_json(), json.dumps(svg)]
        )
    )
    return sign(response)


@app.route('/calculate_individual_MLA', methods=['POST', 'OPTIONS'])
def calculate_individual_MLA():
    if not len(request.data):
        msg = 'no data could be retrieved from your request'
        response = make_response(jsonify(msg))
        return sign(response)
    data = json.loads(request.data)
    main_df, main_byid_df, samples_df, analyses_df = parse_dfs(data)
    (
        Data_Type, sample_list, sigma, uncertainty, best_age_cut_off, 
        U238_decay_constant, U235_decay_constant, U238_U235, 
        excess_variance_206_238, excess_variance_207_206, 
        Sy_calibration_uncertainty_206_238, 
        Sy_calibration_uncertainty_207_206, 
        decay_constant_uncertainty_U238, decay_constant_uncertainty_U235
    ) = parse_params(data)
    ( 
	ages, errors, eight_six_ratios, eight_six_error,
        seven_six_ratios, seven_six_error, numGrains, labels,
	sample_list, best_age_cut_off, dataToLoad_MLA,
	U238_decay_constant,U235_decay_constant,U238_U235,
	excess_variance_206_238, excess_variance_207_206, 
	Sy_calibration_uncertainty_206_238, 
	Sy_calibration_uncertainty_207_206, 
	decay_constant_uncertainty_U238,
	decay_constant_uncertainty_U235
    ) = mdapy.sampleToData(
	sample_list,
	main_byid_df, 
	sigma,
	Data_Type,
	uncertainty,
        best_age_cut_off,
	U238_decay_constant,
	U235_decay_constant,
	U238_U235,excess_variance_206_238,
	excess_variance_207_206,
	Sy_calibration_uncertainty_206_238,
	Sy_calibration_uncertainty_207_206,
	decay_constant_uncertainty_U238, 
	decay_constant_uncertainty_U235
    )

    plotwidth = 10
    plotheight = 7
    age_addition_set_max_plot = 30
    Image_File_Option = 'svg'

    _, table = mdapy.MLA_outputs(sample_list, dataToLoad)
    fname = 'Saved_Files/MLA_Plots/YSP_Plots.svg'

    with open(fname, 'r') as f:
        svg = f.read()
    response = make_response(json.dumps(
            [table.to_json(), json.dumps(svg)]
        )
    )
    # TODO MLA is in the png format and saves in another dir
    return sign(response)


@app.route('/calculate_individual_YDZ', methods=['POST', 'OPTIONS'])
def calculate_individual_YDZ():
    if not len(request.data):
        msg = 'no data could be retrieved from your request'
        response = make_response(jsonify(msg))
        return sign(response)
    data = json.loads(request.data)
    main_df, main_byid_df, samples_df, analyses_df = parse_dfs(data)
    (
        Data_Type, sample_list, sigma, uncertainty, best_age_cut_off, 
        U238_decay_constant, U235_decay_constant, U238_U235, 
        excess_variance_206_238, excess_variance_207_206, 
        Sy_calibration_uncertainty_206_238, 
        Sy_calibration_uncertainty_207_206, 
        decay_constant_uncertainty_U238, decay_constant_uncertainty_U235
    ) = parse_params(data)
    ( 
	ages, errors, eight_six_ratios, eight_six_error,
        seven_six_ratios, seven_six_error, numGrains, labels,
	sample_list, best_age_cut_off, dataToLoad_MLA,
	U238_decay_constant,U235_decay_constant,U238_U235,
	excess_variance_206_238, excess_variance_207_206, 
	Sy_calibration_uncertainty_206_238, 
	Sy_calibration_uncertainty_207_206, 
	decay_constant_uncertainty_U238,
	decay_constant_uncertainty_U235
    ) = mdapy.sampleToData(
	sample_list,
	main_byid_df, 
	sigma,
	Data_Type,
	uncertainty,
        best_age_cut_off,
	U238_decay_constant,
	U235_decay_constant,
	U238_U235,excess_variance_206_238,
	excess_variance_207_206,
	Sy_calibration_uncertainty_206_238,
	Sy_calibration_uncertainty_207_206,
	decay_constant_uncertainty_U238, 
	decay_constant_uncertainty_U235
    )

    YDZ_MDA, minAges, mode = mdapy.YDZ(
        ages, errors, iterations=10000, 
        chartOutput = False, bins=25
    )

    plotwidth = 10
    plotheight = 7
    age_addition_set_max_plot = 30
    Image_File_Option = 'svg'

    _, table = mdapy.YDZ_outputs(
        YDZ_MDA, minAges, mode, ages, errors,
        sample_list, plotwidth, plotheight, 
        Image_File_Option
    )

    fname = 'Saved_Files/Individual_MDA_Plots/YDZ_Plots.svg'
    with open(fname, 'r') as f:
        svg = f.read()
    response = make_response(json.dumps(
            [table.to_json(), json.dumps(svg)]
        )
    )
    return sign(response)


@app.route('/calculate_individual_Y3Zo', methods=['POST', 'OPTIONS'])
def calculate_individual_Y3Zo():
    if not len(request.data):
        msg = 'no data could be retrieved from your request'
        response = make_response(jsonify(msg))
        return sign(response)
    data = json.loads(request.data)
    main_df, main_byid_df, samples_df, analyses_df = parse_dfs(data)
    (
        Data_Type, sample_list, sigma, uncertainty, best_age_cut_off, 
        U238_decay_constant, U235_decay_constant, U238_U235, 
        excess_variance_206_238, excess_variance_207_206, 
        Sy_calibration_uncertainty_206_238, 
        Sy_calibration_uncertainty_207_206, 
        decay_constant_uncertainty_U238, decay_constant_uncertainty_U235
    ) = parse_params(data)
    ( 
	ages, errors, eight_six_ratios, eight_six_error,
        seven_six_ratios, seven_six_error, numGrains, labels,
	sample_list, best_age_cut_off, dataToLoad_MLA,
	U238_decay_constant,U235_decay_constant,U238_U235,
	excess_variance_206_238, excess_variance_207_206, 
	Sy_calibration_uncertainty_206_238, 
	Sy_calibration_uncertainty_207_206, 
	decay_constant_uncertainty_U238,
	decay_constant_uncertainty_U235
    ) = mdapy.sampleToData(
	sample_list,
	main_byid_df, 
	sigma,
	Data_Type,
	uncertainty,
        best_age_cut_off,
	U238_decay_constant,
	U235_decay_constant,
	U238_U235,excess_variance_206_238,
	excess_variance_207_206,
	Sy_calibration_uncertainty_206_238,
	Sy_calibration_uncertainty_207_206,
	decay_constant_uncertainty_U238, 
	decay_constant_uncertainty_U235
    )

    Y3Zo_MDA, Y3Zo_cluster_arrays = mdapy.Y3Zo(
        ages, errors, sample_list, eight_six_ratios,
        eight_six_error, seven_six_ratios, seven_six_error, 
        U238_decay_constant, U235_decay_constant, U238_U235,
        excess_variance_206_238, excess_variance_207_206, 
        Sy_calibration_uncertainty_206_238, 
        Sy_calibration_uncertainty_207_206, 
        decay_constant_uncertainty_U238, 
        decay_constant_uncertainty_U235, 
        Data_Type, best_age_cut_off
    )

    plotwidth = 10
    plotheight = 7
    age_addition_set_max_plot = 30
    Image_File_Option = 'svg'

    _, table = mdapy.Y3Zo_outputs(
        ages, errors, sample_list, Y3Zo_MDA,
        Y3Zo_cluster_arrays, plotwidth, plotheight,
        age_addition_set_max_plot, 
        Image_File_Option, min_cluster_size=3
    )

    fname = 'Saved_Files/Individual_MDA_Plots/Y3Zo_Plots.svg'
    with open(fname, 'r') as f:
        svg = f.read()
    response = make_response(json.dumps(
            [table.to_json(), json.dumps(svg)]
        )
    )
    return sign(response)


@app.route('/calculate_individual_Y3Za', methods=['POST', 'OPTIONS'])
def calculate_individual_Y3Za():
    if not len(request.data):
        msg = 'no data could be retrieved from your request'
        response = make_response(jsonify(msg))
        return sign(response)
    data = json.loads(request.data)
    main_df, main_byid_df, samples_df, analyses_df = parse_dfs(data)
    (
        Data_Type, sample_list, sigma, uncertainty, best_age_cut_off, 
        U238_decay_constant, U235_decay_constant, U238_U235, 
        excess_variance_206_238, excess_variance_207_206, 
        Sy_calibration_uncertainty_206_238, 
        Sy_calibration_uncertainty_207_206, 
        decay_constant_uncertainty_U238, decay_constant_uncertainty_U235
    ) = parse_params(data)
    ( 
        ages, errors, eight_six_ratios, eight_six_error,
        seven_six_ratios, seven_six_error, numGrains, labels,
        sample_list, best_age_cut_off, dataToLoad_MLA,
        U238_decay_constant,U235_decay_constant,U238_U235,
        excess_variance_206_238, excess_variance_207_206, 
        Sy_calibration_uncertainty_206_238, 
        Sy_calibration_uncertainty_207_206, 
        decay_constant_uncertainty_U238,
        decay_constant_uncertainty_U235
    ) = mdapy.sampleToData(
        sample_list,
        main_byid_df, 
        sigma,
        Data_Type,
        uncertainty,
        best_age_cut_off,
        U238_decay_constant,
        U235_decay_constant,
        U238_U235,excess_variance_206_238,
        excess_variance_207_206,
        Sy_calibration_uncertainty_206_238,
        Sy_calibration_uncertainty_207_206,
        decay_constant_uncertainty_U238, 
        decay_constant_uncertainty_U235
    )

    Y3Za_MDA, Y3Za_cluster_arrays = mdapy.Y3Za(
        ages, errors, sample_list,
        eight_six_ratios, eight_six_error, seven_six_ratios,
        seven_six_error, U238_decay_constant, U235_decay_constant,
        U238_U235, excess_variance_206_238, excess_variance_207_206,
        Sy_calibration_uncertainty_206_238,
        Sy_calibration_uncertainty_207_206,
        decay_constant_uncertainty_U238,
        decay_constant_uncertainty_U235,
        Data_Type, best_age_cut_off
    )

    plotwidth = 10
    plotheight = 7
    age_addition_set_max_plot = 30
    Image_File_Option = 'svg'

    _, table = mdapy.Y3Za_outputs(
        ages, errors, Y3Za_MDA, Y3Za_cluster_arrays,
        sample_list, plotwidth, plotheight, 
        age_addition_set_max_plot, Image_File_Option
    )

    fname = 'Saved_Files/Individual_MDA_Plots/Y3Za_Plots.svg'
    with open(fname, 'r') as f:
        svg = f.read()
    response = make_response(json.dumps(
            [table.to_json(), json.dumps(svg)]
        )
    )
    return sign(response)


# PLOT ALL SAMPLES WITH ONE MDA METHOD

@app.route('/calculate_all_samples_YC1s', methods=['POST', 'OPTIONS'])
def calculate_all_samples_YC1s():
    if not len(request.data):
        msg = 'no data could be retrieved from your request'
        response = make_response(jsonify(msg))
        return sign(response)
    data = json.loads(request.data)
    main_df, main_byid_df, samples_df, analyses_df = parse_dfs(data)
    (
        Data_Type, sample_list, sigma, uncertainty, best_age_cut_off, 
        U238_decay_constant, U235_decay_constant, U238_U235, 
        excess_variance_206_238, excess_variance_207_206, 
        Sy_calibration_uncertainty_206_238, Sy_calibration_uncertainty_207_206, 
        decay_constant_uncertainty_U238, decay_constant_uncertainty_U235
    ) = parse_params(data)
    ( 
        ages, errors, eight_six_ratios, eight_six_error,
        seven_six_ratios, seven_six_error, numGrains, labels,
        sample_list, best_age_cut_off, dataToLoad_MLA,
        U238_decay_constant,U235_decay_constant,U238_U235,
        excess_variance_206_238, excess_variance_207_206, 
        Sy_calibration_uncertainty_206_238, 
        Sy_calibration_uncertainty_207_206, 
        decay_constant_uncertainty_U238,
        decay_constant_uncertainty_U235
    ) = mdapy.sampleToData(
        sample_list,
        main_byid_df, 
        sigma,
        Data_Type,
        uncertainty,
        best_age_cut_off,
        U238_decay_constant,
        U235_decay_constant,
        U238_U235,excess_variance_206_238,
        excess_variance_207_206,
        Sy_calibration_uncertainty_206_238,
        Sy_calibration_uncertainty_207_206,
        decay_constant_uncertainty_U238, 
        decay_constant_uncertainty_U235
    )

    YC1s_MDA, YC1s_cluster_arrays = mdapy.YC1s(ages, errors, sample_list, eight_six_ratios, eight_six_error, seven_six_ratios, seven_six_error, U238_decay_constant, U235_decay_constant, U238_U235, excess_variance_206_238, excess_variance_207_206, Sy_calibration_uncertainty_206_238, Sy_calibration_uncertainty_207_206, decay_constant_uncertainty_U238, decay_constant_uncertainty_U235, Data_Type, best_age_cut_off, min_cluster_size=2)

    plotwidth = 10
    plotheight = 7
    age_addition_set_max_plot = 30
    Image_File_Option = 'svg'

    mdapy.YC1s_Strat_Plot(YC1s_MDA, sample_list, Image_File_Option, plotwidth, plotheight)

    fname = 'Saved_Files/Stratigraphic_Plots/YC1s_All_Samples_Plot.svg'
    with open(fname, 'r') as f:
        svg = f.read()
    response = make_response(json.dumps([json.dumps(svg)]))
    return sign(response)


@app.route('/calculate_all_samples_YC2s', methods=['POST', 'OPTIONS'])
def calculate_all_samples_YC2s():
    if not len(request.data):
        msg = 'no data could be retrieved from your request'
        response = make_response(jsonify(msg))
        return sign(response)
    data = json.loads(request.data)
    main_df, main_byid_df, samples_df, analyses_df = parse_dfs(data)
    (
        Data_Type, sample_list, sigma, uncertainty, best_age_cut_off, 
        U238_decay_constant, U235_decay_constant, U238_U235, 
        excess_variance_206_238, excess_variance_207_206, 
        Sy_calibration_uncertainty_206_238, Sy_calibration_uncertainty_207_206, 
        decay_constant_uncertainty_U238, decay_constant_uncertainty_U235
    ) = parse_params(data)
    ( 
	ages, errors, eight_six_ratios, eight_six_error,
        seven_six_ratios, seven_six_error, numGrains, labels,
	sample_list, best_age_cut_off, dataToLoad_MLA,
	U238_decay_constant,U235_decay_constant,U238_U235,
	excess_variance_206_238, excess_variance_207_206, 
	Sy_calibration_uncertainty_206_238, 
	Sy_calibration_uncertainty_207_206, 
	decay_constant_uncertainty_U238,
	decay_constant_uncertainty_U235
    ) = mdapy.sampleToData(
	sample_list,
	main_byid_df, 
	sigma,
	Data_Type,
	uncertainty,
        best_age_cut_off,
	U238_decay_constant,
	U235_decay_constant,
	U238_U235,excess_variance_206_238,
	excess_variance_207_206,
	Sy_calibration_uncertainty_206_238,
	Sy_calibration_uncertainty_207_206,
	decay_constant_uncertainty_U238, 
	decay_constant_uncertainty_U235
    )
    YC2s_MDA,YC2s_cluster_arrays = mdapy.YC2s(ages, errors, sample_list, eight_six_ratios, eight_six_error, seven_six_ratios, seven_six_error, U238_decay_constant, U235_decay_constant, U238_U235, excess_variance_206_238, excess_variance_207_206, Sy_calibration_uncertainty_206_238, Sy_calibration_uncertainty_207_206, decay_constant_uncertainty_U238, decay_constant_uncertainty_U235, Data_Type, best_age_cut_off, min_cluster_size=3)

    plotwidth = 10
    plotheight = 7
    age_addition_set_max_plot = 30
    Image_File_Option = 'svg'

    mdapy.YC2s_Strat_Plot(YC2s_MDA, sample_list, Image_File_Option, plotwidth, plotheight)

    fname = 'Saved_Files/Stratigraphic_Plots/YC2s_All_Samples_Plot.svg'
    with open(fname, 'r') as f:
        svg = f.read()
    response = make_response(json.dumps([json.dumps(svg)]))
    return sign(response)


@app.route('/calculate_all_samples_Tau', methods=['POST', 'OPTIONS'])
def calculate_all_samples_Tau():
    if not len(request.data):
        msg = 'no data could be retrieved from your request'
        response = make_response(jsonify(msg))
        return sign(response)
    data = json.loads(request.data)
    main_df, main_byid_df, samples_df, analyses_df = parse_dfs(data)
    (
        Data_Type, sample_list, sigma, uncertainty, best_age_cut_off, 
        U238_decay_constant, U235_decay_constant, U238_U235, 
        excess_variance_206_238, excess_variance_207_206, 
        Sy_calibration_uncertainty_206_238, Sy_calibration_uncertainty_207_206, 
        decay_constant_uncertainty_U238, decay_constant_uncertainty_U235
    ) = parse_params(data)
    ( 
	ages, errors, eight_six_ratios, eight_six_error,
        seven_six_ratios, seven_six_error, numGrains, labels,
	sample_list, best_age_cut_off, dataToLoad_MLA,
	U238_decay_constant,U235_decay_constant,U238_U235,
	excess_variance_206_238, excess_variance_207_206, 
	Sy_calibration_uncertainty_206_238, 
	Sy_calibration_uncertainty_207_206, 
	decay_constant_uncertainty_U238,
	decay_constant_uncertainty_U235
    ) = mdapy.sampleToData(
	sample_list,
	main_byid_df, 
	sigma,
	Data_Type,
	uncertainty,
        best_age_cut_off,
	U238_decay_constant,
	U235_decay_constant,
	U238_U235,excess_variance_206_238,
	excess_variance_207_206,
	Sy_calibration_uncertainty_206_238,
	Sy_calibration_uncertainty_207_206,
	decay_constant_uncertainty_U238, 
	decay_constant_uncertainty_U235
    )
    Tau_MDA, Tau_Grains, PDP_age, PDP, plot_max, ages_errors1s_filtered, tauMethod_WM,tauMethod_WM_err2s = mdapy.tau(ages, errors, sample_list, eight_six_ratios, eight_six_error, seven_six_ratios, seven_six_error, U238_decay_constant, U235_decay_constant, U238_U235, excess_variance_206_238, excess_variance_207_206, Sy_calibration_uncertainty_206_238, Sy_calibration_uncertainty_207_206, decay_constant_uncertainty_U238, decay_constant_uncertainty_U235, Data_Type, best_age_cut_off, min_cluster_size=3, thres=0.01, minDist=1, xdif=1, x1=0, x2=4000)

    plotwidth = 10
    plotheight = 7
    age_addition_set_max_plot = 30
    Image_File_Option = 'svg'

    mdapy.Tau_Strat_Plot(Tau_MDA, sample_list, Image_File_Option, plotwidth, plotheight)

    fname = 'Saved_Files/Stratigraphic_Plots/Tau_All_Samples_Plot.svg'
    with open(fname, 'r') as f:
        svg = f.read()
    response = make_response(json.dumps([json.dumps(svg)]))
    return sign(response)


@app.route('/calculate_all_samples_YSP', methods=['POST', 'OPTIONS'])
def calculate_all_samples_YSP():
    if not len(request.data):
        msg = 'no data could be retrieved from your request'
        response = make_response(jsonify(msg))
        return sign(response)
    data = json.loads(request.data)
    main_df, main_byid_df, samples_df, analyses_df = parse_dfs(data)
    (
        Data_Type, sample_list, sigma, uncertainty, best_age_cut_off, 
        U238_decay_constant, U235_decay_constant, U238_U235, 
        excess_variance_206_238, excess_variance_207_206, 
        Sy_calibration_uncertainty_206_238, Sy_calibration_uncertainty_207_206, 
        decay_constant_uncertainty_U238, decay_constant_uncertainty_U235
    ) = parse_params(data)
    ( 
	ages, errors, eight_six_ratios, eight_six_error,
        seven_six_ratios, seven_six_error, numGrains, labels,
	sample_list, best_age_cut_off, dataToLoad_MLA,
	U238_decay_constant,U235_decay_constant,U238_U235,
	excess_variance_206_238, excess_variance_207_206, 
	Sy_calibration_uncertainty_206_238, 
	Sy_calibration_uncertainty_207_206, 
	decay_constant_uncertainty_U238,
	decay_constant_uncertainty_U235
    ) = mdapy.sampleToData(
	sample_list,
	main_byid_df, 
	sigma,
	Data_Type,
	uncertainty,
        best_age_cut_off,
	U238_decay_constant,
	U235_decay_constant,
	U238_U235,excess_variance_206_238,
	excess_variance_207_206,
	Sy_calibration_uncertainty_206_238,
	Sy_calibration_uncertainty_207_206,
	decay_constant_uncertainty_U238, 
	decay_constant_uncertainty_U235
    )

    YSP_MDA, YSP_cluster = mdapy.YSP(ages, errors, sample_list, eight_six_ratios, eight_six_error, seven_six_ratios, seven_six_error, U238_decay_constant, U235_decay_constant, U238_U235, excess_variance_206_238, excess_variance_207_206, Sy_calibration_uncertainty_206_238, Sy_calibration_uncertainty_207_206, decay_constant_uncertainty_U238, decay_constant_uncertainty_U235, Data_Type, best_age_cut_off, min_cluster_size=2, MSWD_threshold=1)

    plotwidth = 10
    plotheight = 7
    age_addition_set_max_plot = 30
    Image_File_Option = 'svg'

    mdapy.YSP_Strat_Plot(YSP_MDA, sample_list, Image_File_Option, plotwidth, plotheight)

    fname = 'Saved_Files/Stratigraphic_Plots/YSP_All_Samples_Plot.svg'
    with open(fname, 'r') as f:
        svg = f.read()
    response = make_response(json.dumps([json.dumps(svg)]))
    return sign(response)


@app.route('/calculate_all_samples_YDZ', methods=['POST', 'OPTIONS'])
def calculate_all_samples_YDZ():
    if not len(request.data):
        msg = 'no data could be retrieved from your request'
        response = make_response(jsonify(msg))
        return sign(response)
    data = json.loads(request.data)
    main_df, main_byid_df, samples_df, analyses_df = parse_dfs(data)
    (
        Data_Type, sample_list, sigma, uncertainty, best_age_cut_off, 
        U238_decay_constant, U235_decay_constant, U238_U235, 
        excess_variance_206_238, excess_variance_207_206, 
        Sy_calibration_uncertainty_206_238, Sy_calibration_uncertainty_207_206, 
        decay_constant_uncertainty_U238, decay_constant_uncertainty_U235
    ) = parse_params(data)
    ( 
	ages, errors, eight_six_ratios, eight_six_error,
        seven_six_ratios, seven_six_error, numGrains, labels,
	sample_list, best_age_cut_off, dataToLoad_MLA,
	U238_decay_constant,U235_decay_constant,U238_U235,
	excess_variance_206_238, excess_variance_207_206, 
	Sy_calibration_uncertainty_206_238, 
	Sy_calibration_uncertainty_207_206, 
	decay_constant_uncertainty_U238,
	decay_constant_uncertainty_U235
    ) = mdapy.sampleToData(
	sample_list,
	main_byid_df, 
	sigma,
	Data_Type,
	uncertainty,
        best_age_cut_off,
	U238_decay_constant,
	U235_decay_constant,
	U238_U235,excess_variance_206_238,
	excess_variance_207_206,
	Sy_calibration_uncertainty_206_238,
	Sy_calibration_uncertainty_207_206,
	decay_constant_uncertainty_U238, 
	decay_constant_uncertainty_U235
    )

    YDZ_MDA, minAges, mode = mdapy.YDZ(ages, errors, iterations=10000, chartOutput = False, bins=25)

    plotwidth = 10
    plotheight = 7
    age_addition_set_max_plot = 30
    Image_File_Option = 'svg'

    mdapy.YDZ_Strat_Plot(YDZ_MDA, sample_list, Image_File_Option, plotwidth, plotheight)

    fname = 'Saved_Files/Stratigraphic_Plots/YDZ_All_Samples_Plot.svg'
    with open(fname, 'r') as f:
        svg = f.read()
    response = make_response(json.dumps([json.dumps(svg)]))
    return sign(response)


@app.route('/calculate_all_samples_Y3Zo', methods=['POST', 'OPTIONS'])
def calculate_all_samples_Y3Zo():
    if not len(request.data):
        msg = 'no data could be retrieved from your request'
        response = make_response(jsonify(msg))
        return sign(response)
    data = json.loads(request.data)
    main_df, main_byid_df, samples_df, analyses_df = parse_dfs(data)
    (
        Data_Type, sample_list, sigma, uncertainty, best_age_cut_off, 
        U238_decay_constant, U235_decay_constant, U238_U235, 
        excess_variance_206_238, excess_variance_207_206, 
        Sy_calibration_uncertainty_206_238, Sy_calibration_uncertainty_207_206, 
        decay_constant_uncertainty_U238, decay_constant_uncertainty_U235
    ) = parse_params(data)
    ( 
	ages, errors, eight_six_ratios, eight_six_error,
        seven_six_ratios, seven_six_error, numGrains, labels,
	sample_list, best_age_cut_off, dataToLoad_MLA,
	U238_decay_constant,U235_decay_constant,U238_U235,
	excess_variance_206_238, excess_variance_207_206, 
	Sy_calibration_uncertainty_206_238, 
	Sy_calibration_uncertainty_207_206, 
	decay_constant_uncertainty_U238,
	decay_constant_uncertainty_U235
    ) = mdapy.sampleToData(
	sample_list,
	main_byid_df, 
	sigma,
	Data_Type,
	uncertainty,
        best_age_cut_off,
	U238_decay_constant,
	U235_decay_constant,
	U238_U235,excess_variance_206_238,
	excess_variance_207_206,
	Sy_calibration_uncertainty_206_238,
	Sy_calibration_uncertainty_207_206,
	decay_constant_uncertainty_U238, 
	decay_constant_uncertainty_U235
    )
    Y3Zo_MDA, Y3Zo_cluster_arrays = mdapy.Y3Zo(ages, errors, sample_list, eight_six_ratios, eight_six_error, seven_six_ratios, seven_six_error, U238_decay_constant, U235_decay_constant, U238_U235, excess_variance_206_238, excess_variance_207_206, Sy_calibration_uncertainty_206_238, Sy_calibration_uncertainty_207_206, decay_constant_uncertainty_U238, decay_constant_uncertainty_U235, Data_Type, best_age_cut_off)

    plotwidth = 10
    plotheight = 7
    age_addition_set_max_plot = 30
    Image_File_Option = 'svg'

    mdapy.Y3Zo_Strat_Plot(Y3Zo_MDA, sample_list, Image_File_Option, plotwidth, plotheight)

    fname = 'Saved_Files/Stratigraphic_Plots/Y3Zo_All_Samples_Plot.svg'
    with open(fname, 'r') as f:
        svg = f.read()
    response = make_response(json.dumps([json.dumps(svg)]))
    return sign(response)


@app.route('/calculate_all_samples_Y3Za', methods=['POST', 'OPTIONS'])
def calculate_all_samples_Y3Za():
    if not len(request.data):
        msg = 'no data could be retrieved from your request'
        response = make_response(jsonify(msg))
        return sign(response)
    data = json.loads(request.data)
    main_df, main_byid_df, samples_df, analyses_df = parse_dfs(data)
    (
        Data_Type, sample_list, sigma, uncertainty, best_age_cut_off, 
        U238_decay_constant, U235_decay_constant, U238_U235, 
        excess_variance_206_238, excess_variance_207_206, 
        Sy_calibration_uncertainty_206_238, Sy_calibration_uncertainty_207_206, 
        decay_constant_uncertainty_U238, decay_constant_uncertainty_U235
    ) = parse_params(data)
    ( 
	ages, errors, eight_six_ratios, eight_six_error,
        seven_six_ratios, seven_six_error, numGrains, labels,
	sample_list, best_age_cut_off, dataToLoad_MLA,
	U238_decay_constant,U235_decay_constant,U238_U235,
	excess_variance_206_238, excess_variance_207_206, 
	Sy_calibration_uncertainty_206_238, 
	Sy_calibration_uncertainty_207_206, 
	decay_constant_uncertainty_U238,
	decay_constant_uncertainty_U235
    ) = mdapy.sampleToData(
	sample_list,
	main_byid_df, 
	sigma,
	Data_Type,
	uncertainty,
        best_age_cut_off,
	U238_decay_constant,
	U235_decay_constant,
	U238_U235,excess_variance_206_238,
	excess_variance_207_206,
	Sy_calibration_uncertainty_206_238,
	Sy_calibration_uncertainty_207_206,
	decay_constant_uncertainty_U238, 
	decay_constant_uncertainty_U235
    )
    Y3Za_MDA, Y3Za_cluster_arrays = mdapy.Y3Za(
        ages, errors, sample_list,
        eight_six_ratios, eight_six_error, seven_six_ratios,
        seven_six_error, U238_decay_constant, U235_decay_constant,
        U238_U235, excess_variance_206_238, excess_variance_207_206,
        Sy_calibration_uncertainty_206_238,
        Sy_calibration_uncertainty_207_206,
        decay_constant_uncertainty_U238, decay_constant_uncertainty_U235,
        Data_Type, best_age_cut_off
    )

    plotwidth = 10
    plotheight = 7
    age_addition_set_max_plot = 30
    Image_File_Option = 'svg'
    mdapy.Y3Za_Strat_Plot(Y3Za_MDA, sample_list, Image_File_Option, plotwidth, plotheight)

    fname = 'Saved_Files/Stratigraphic_Plots/Y3Za_All_Samples_Plot.svg'
    with open(fname, 'r') as f:
        svg = f.read()
    response = make_response(json.dumps([json.dumps(svg)]))
    return sign(response)


@app.route('/calculate_all_samples_YSG', methods=['POST', 'OPTIONS'])
def calculate_all_samples_YSG():
    if not len(request.data):
        msg = 'no data could be retrieved from your request'
        response = make_response(jsonify(msg))
        return sign(response)
    data = json.loads(request.data)
    main_df, main_byid_df, samples_df, analyses_df = parse_dfs(data)
    (
        Data_Type, sample_list, sigma, uncertainty, best_age_cut_off, 
        U238_decay_constant, U235_decay_constant, U238_U235, 
        excess_variance_206_238, excess_variance_207_206, 
        Sy_calibration_uncertainty_206_238, Sy_calibration_uncertainty_207_206, 
        decay_constant_uncertainty_U238, decay_constant_uncertainty_U235
    ) = parse_params(data)
    ( 
	ages, errors, eight_six_ratios, eight_six_error,
        seven_six_ratios, seven_six_error, numGrains, labels,
	sample_list, best_age_cut_off, dataToLoad_MLA,
	U238_decay_constant,U235_decay_constant,U238_U235,
	excess_variance_206_238, excess_variance_207_206, 
	Sy_calibration_uncertainty_206_238, 
	Sy_calibration_uncertainty_207_206, 
	decay_constant_uncertainty_U238,
	decay_constant_uncertainty_U235
    ) = mdapy.sampleToData(
	sample_list,
	main_byid_df, 
	sigma,
	Data_Type,
	uncertainty,
        best_age_cut_off,
	U238_decay_constant,
	U235_decay_constant,
	U238_U235,excess_variance_206_238,
	excess_variance_207_206,
	Sy_calibration_uncertainty_206_238,
	Sy_calibration_uncertainty_207_206,
	decay_constant_uncertainty_U238, 
	decay_constant_uncertainty_U235
    )

    YSG_MDA = mdapy.YSG(
        ages, errors, sample_list, excess_variance_206_238,
        excess_variance_207_206, Sy_calibration_uncertainty_206_238,
        Sy_calibration_uncertainty_207_206,
        decay_constant_uncertainty_U238,
        decay_constant_uncertainty_U235, Data_Type, best_age_cut_off
    )

    plotwidth = 10
    plotheight = 7
    age_addition_set_max_plot = 30
    Image_File_Option = 'svg'
    mdapy.YSG_Strat_Plot(YSG_MDA, sample_list, Image_File_Option, plotwidth, plotheight)

    fname = 'Saved_Files/Stratigraphic_Plots/YSG_All_Samples_Plot.svg'
    with open(fname, 'r') as f:
        svg = f.read()
    response = make_response(json.dumps([json.dumps(svg)]))
    return sign(response)

