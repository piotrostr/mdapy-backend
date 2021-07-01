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
    sample_list = ['UK027', 'UK026']  # where to get this from? TODO
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


def parse_dfs(data):
    """
    :returns tuple: main_df, main_byid_df, samples_df, analyses_df 
    """
    arrays = data['table']['data']
    arrays = [[i['value'] for i in row] for row in arrays]
    column_names = data['table']['columnLabels']
    print(column_names)
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
    print(mda.__dir__())
    return jsonify('MDAPy API home')


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

    print(parse_dfs(data))
    dataToLoad_MLA = ['Data/_.xlsx']  # bypass the excel save-requiring bug
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

    mdapy.Plot_MDA(
        MDAs_1s_table, all_MDA_data, sample_list, YSG_MDA, YC1s_MDA, 
        YC2s_MDA, YDZ_MDA, Y3Zo_MDA, Y3Za_MDA, Tau_MDA, YSP_MDA, YPP_MDA, 
        MLA_MDA, Image_File_Option, plotwidth, plotheight
    )

    fname = 'Saved_Files/All_MDA_Methods_Plots/All_MDA_Methods_Plots.svg'
    with open(fname, 'r') as f:
        svg = f.read()
    response = make_response([MDAs_1s_table.to_json(), json.dumps(svg)])
    return response
    
    # the above gets ALL the data for each of the individual plots, to be used for method #1
    # each of the charts and tables for methods #2, #3 can be made using the data from #1
    # hence I think Ill just split the methods so each is retrieved from a separate enpoint to speed it up
    # but 
    # Ill implement method #1 and #3 first as they use the same data, to be retrieved from the same endpoint

    # method #1:
    # mdapy.MDA_Calculator -> mdapy.Plot_MDA -> All_MDA_Methods_Plots.svg 

    #  ! problem with the above is that the plot contains all the plots at 
    #    once, while we need those split in fe

    # method #3:
    # mdapy.MDA_Calculator -> mdapy.MDA_Strat_Plot -> Stratigraphic_Plots/*.svg
    # for now only YSG is working

