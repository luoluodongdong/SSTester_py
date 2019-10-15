import os
#import pytest
import json
import pypudding
import time
from datetime import datetime
from pypudding import IPUUT, IPTestSpec, IPTestResult, InstantPuddingError
import sys


def setup_module(module):
    # refresh station_health_check.json timestamp to resolve InstantPudding commit error
    config = '/vault/data_collection/test_station_config/station_health_check.json'
    if not os.path.exists(config):
        sys.exit('file not exists')

    now = int(time.time())
    str_now = datetime.strftime(datetime.fromtimestamp(now), '%Y-%m-%d %H:%M:%S')

    # js = None
    with open(config, 'rU') as src:
        js = json.load(src, encoding='ascii')
        for key, val in js.iteritems():
            if val == 0 or val == 1:
                continue
            if type(val) is int:
                js[key] = now
            else:
                js[key] = str_now
    with open(config, 'w') as dst:
        dst.writelines(json.dumps(js, sort_keys=True, indent=4))

#@pytest.fixture(scope='module')


def station_info():
    fp = open('/vault/data_collection/test_station_config/gh_station_info.json')
    config = json.load(fp)
    return config['ghinfo']


#@pytest.fixture
def uut():
    uut = IPUUT()
    uut.start()
    uut.add_attribute(pypudding.IP_ATTRIBUTE_STATIONSOFTWARENAME, "PyPudding")
    uut.add_attribute(pypudding.IP_ATTRIBUTE_STATIONSOFTWAREVERSION, '1.1')
    return uut


def test_read_station_info(station_info):
    gh_station = pypudding.IPGHStation()
    station_type = gh_station[pypudding.IP_STATION_TYPE]
    assert station_type == station_info['STATION_TYPE']
    assert gh_station[pypudding.IP_STATION_NUMBER] == station_info['STATION_NUMBER']


def test_commit_run():
    uut = IPUUT(u'C076535001NHP5L3')

    uut.start()
    uut.add_attribute(pypudding.IP_ATTRIBUTE_STATIONSOFTWARENAME, u"PyPudding")
    uut.add_attribute(pypudding.IP_ATTRIBUTE_STATIONSOFTWAREVERSION, u'1.1')

    # pass fail test passing:
    spec = IPTestSpec('PassingTest')
    result = IPTestResult(pypudding.IP_PASS)
    uut.add_result(spec, result)

    # parametric test pass
    spec = IPTestSpec(u'Parametric data test', subtest_name='pass_test',
                      limits={'low_limit': 0, 'high_limit': 9}, unit=u'ly')
    result = IPTestResult(pypudding.IP_PASS, 4)
    uut.add_result(spec, result)

    # parametric test fail
    spec = IPTestSpec(u'Parametric data test', subtest_name=u'fail_test',
                      limits={'low_limit': 0, 'high_limit': 8}, unit='ly')
    result = IPTestResult(pypudding.IP_FAIL, 11, u'value out of range')
    uut.add_result(spec, result)
    uut.add_attribute(u'VBOOST_LEFT', u'0x01')

    path = os.path.split(__file__)[0]
    print(path)
    plan_path = os.path.join(path, 'pypudding.py')
    uut.add_blob_file(u'myself', plan_path)
    uut.done()
    uut.commit(pypudding.IP_PASS)
    reply = pypudding.IP_getJsonResultsObj(uut.uut)
    msg = pypudding.IP_reply_getError(reply)
    commit_obj = json.loads(msg)

    print commit_obj['blobs']
    blobs = commit_obj['blobs']
    assert len(blobs) == 1
    assert blobs[0]['display_name'] == 'myself'

    s_attr = commit_obj['test_station_attributes']
    assert s_attr['software_name'] == 'PyPudding'
    assert s_attr['software_version'] == '1.1'

    u_attr = commit_obj['uut_attributes']
    assert u_attr.keys() == ['VBOOST_LEFT']
    assert u_attr['VBOOST_LEFT'] == '0x01'
    t_attr = commit_obj['test_attributes']
    assert t_attr['unit_serial_number'] == 'C076535001NHP5L3'
    results = commit_obj['results']
    real_results = [r for r in results if r['test'] != 'FATAL ERROR']
    assert len(real_results) == 3

    r0 = real_results[0]
    assert r0['test'] == 'PassingTest'
    assert r0['test_type'] == 'PF'
    assert r0['result'] == 'pass'

    r1 = real_results[1]
    assert r1['test'] == 'Parametric data test'
    assert r1['sub_test'] == 'pass_test'
    assert r1['parametric_key'] == 'Parametric data test pass_test'
    assert r1['result'] == 'pass'
    assert r1['lower_limit'] == '0'
    assert r1['upper_limit'] == '9'
    assert r1['value'] == '4'

    r2 = real_results[2]
    assert r2['test'] == 'Parametric data test'
    assert r2['sub_test'] == 'fail_test'
    assert r2['parametric_key'] == 'Parametric data test fail_test'
    assert r2['result'] == 'fail'
    assert r2['lower_limit'] == '0'
    assert r2['upper_limit'] == '8'
    assert r2['value'] == '11'

    pypudding.IP_reply_destroy(reply)
    del uut
    print('done.')


def test_name_too_long(uut):
    # InstantPudding.log shows an error and the result is NOT in the committed JSON file
    uut.set_sn('C0770140016HP5H4')

    long_name = 'n' * (pypudding.PDCA_TEST_NAME_MAX_LEN + 1)
    with pytest.raises(InstantPuddingError) as exc:
        spec = IPTestSpec(long_name, subtest_name='pass_test', limits={'low_limit': 0, 'high_limit': 9}, unit='ly')
    assert exc.value.message.startswith("test name is too long")

    long_name = 'n' * (pypudding.PDCA_SUBTEST_NAME_MANX_LEN + 1)
    with pytest.raises(InstantPuddingError) as exc:
        spec = IPTestSpec('passing_test', subtest_name=long_name, limits={'low_limit': 0, 'high_limit': 9}, unit='ly')
    assert exc.value.message.startswith("subtest name is too long")

    long_name = 'n' * (pypudding.PDCA_SUBSUBTEST_NAME_MANX_LEN + 1)
    with pytest.raises(InstantPuddingError) as exc:
        spec = IPTestSpec('passing_test', subtest_name='passing sub test',
                          subsubtest_name=long_name, limits={'low_limit': 0, 'high_limit': 9}, unit='ly')
    assert exc.value.message.startswith("subsubtest name is too long")

    long_name = 'n' * (pypudding.PDCA_UNIT_MAX_LEN + 1)
    with pytest.raises(InstantPuddingError) as exc:
        spec = IPTestSpec('passing_test', subtest_name='passing sub test',
                          limits={'low_limit':0, 'high_limit': 9}, unit=long_name)
    assert exc.value.message.startswith("unit is too long")

    long_msg = 'n' * (pypudding.PDCA_FAIL_MSG_MAX_LEN + 1)
    with pytest.raises(InstantPuddingError) as exc:
        r = IPTestResult(pypudding.IP_FAIL, message=long_msg)
    assert exc.value.message.startswith("fail message is too long")

    long_name = 'n' * (pypudding.PDCA_ATTRIBUTE_NAME_MAX_LEN + 1)
    with pytest.raises(InstantPuddingError) as exc:
        uut.add_attribute(long_name, 'some value')
    assert exc.value.message.startswith("attribute name is too long")

    long_value = 'n' * (pypudding.PDCA_ATTRIBUTE_VALUE_MAX_LEN + 1)
    with pytest.raises(InstantPuddingError) as exc:
        uut.add_attribute('some attribute', long_value)
    assert exc.value.message.startswith("attribute value is too long")

    uut.cancel()
    del uut


def test_no_fail_message(uut):
    # instant pudding log shows an error but the result is in the committed JSON file
    uut.set_sn('C0770140016HP5H5')

    long_name = 'no_fail_msg'
    spec = IPTestSpec(long_name, subtest_name='pass_test', limits={'low_limit': 0, 'high_limit': 9}, unit='ly')
    result = IPTestResult(pypudding.IP_FAIL, -3)
    assert result._message == 'FAIL'  # a default fail message is added
    result.message = 'my message'
    assert result._message == 'my message'
    result = IPTestResult(pypudding.IP_FAIL, -3, 'my message 2')
    assert result._message == 'my message 2'
    result.set_result(pypudding.IP_FAIL)
    assert result._message == 'my message 2'  # my message is not overwritten

    uut.cancel()
    del uut


def test_numeric_format(uut):
    # instant pudding log shows an error but the result is in the committed JSON file
    uut.set_sn('C0770140016HP5H6')
    # valid numerical values
    spec = IPTestSpec('test name', 'subtest_name', limits={'low_limit': '.4', 'high_limit': '-12e-3'})
    with pytest.raises(InstantPuddingError) as exc:
        spec = IPTestSpec('test name', 'subtest_name', limits={'low_limit': '0x45', 'high_limit':'-12e-3'})
    assert exc.value.message.endswith("is not a numerical value accepted by PDCA")

    result = IPTestResult(pypudding.IP_PASS, '+.3e2')
    with pytest.raises(InstantPuddingError) as exc:
        result = IPTestResult(pypudding.IP_PASS, '2fe3')
    assert exc.value.message.endswith("is not a numerical value accepted by PDCA")
    uut.cancel()
    del uut


def test_no_sn(uut):
    uut.start()
    uut.add_attribute(pypudding.IP_ATTRIBUTE_STATIONSOFTWARENAME, u"PyPudding")
    uut.add_attribute(pypudding.IP_ATTRIBUTE_STATIONSOFTWAREVERSION, u'1.1')

    spec = IPTestSpec(u'Parametric data test', subtest_name='pass_test', limits={'low_limit':0, 'high_limit':9}, unit=u'ly')
    result = IPTestResult(pypudding.IP_PASS, 4)
    uut.add_result(spec, result)

    try:
        uut.done()  # if IP_MSG_ERROR_API_SYNTAX is turned on, calling Done with an SN triggers an error as well.
    except InstantPuddingError:
        pass

    with pytest.raises(InstantPuddingError) as exc:

        uut.commit(pypudding.IP_PASS)
    assert exc.value.message.endswith("trying to commit without an SN")

    uut.cancel()
    del uut


def test_validate_serial_number():
    assert pypudding.validate_serial_number("C076535001NHP5L3")
    assert not pypudding.validate_serial_number(None)
    assert not pypudding.validate_serial_number('123456789')
    assert not pypudding.validate_serial_number('')
    assert not pypudding.validate_serial_number(1)
    assert not pypudding.validate_serial_number('\xe5\xba\x8f\xe5\x88\x97\xe5\x8f\xb7')
    assert pypudding.validate_serial_number(u'FN664640GMAHTCM1G')
    assert pypudding.validate_serial_number('FN664640GMAHTCM1G')
    # Invalid serial number will only be caught if IP_MSG_ERROR_INVALID_SERIAL_NUMBER is 1 in the parachute session of ghstationinfo.json


def test_NA_limit():
    uut = IPUUT(u'C076535001NHP5L3')

    uut.start()
    uut.add_attribute(pypudding.IP_ATTRIBUTE_STATIONSOFTWARENAME, u"PyPudding")
    uut.add_attribute(pypudding.IP_ATTRIBUTE_STATIONSOFTWAREVERSION, u'1.1')

    # parametric test pass
    spec = IPTestSpec(u'Parametric data test pass', subtest_name='No_High_limit',
                      limits={'low_limit': 0, 'high_limit': 'NA'}, unit=u'ly')
    result = IPTestResult(pypudding.IP_PASS, 4)
    uut.add_result(spec, result)

    # parametric test fail
    spec = IPTestSpec(u'Parametric data test fail', subtest_name=u'No_Low_Limit',
                      limits={'low_limit': 'NA', 'high_limit': 8}, unit='ly')
    result = IPTestResult(pypudding.IP_FAIL, 11, u'value out of range')
    uut.add_result(spec, result)
    uut.done()
    uut.commit(pypudding.IP_PASS)
    reply = pypudding.IP_getJsonResultsObj(uut.uut)
    msg = pypudding.IP_reply_getError(reply)
    commit_obj = json.loads(msg)

    results = commit_obj['results']
    real_results = [r for r in results if r['test'] != 'FATAL ERROR']
    assert len(real_results) == 2

    r0 = real_results[0]
    assert r0['sub_test'] == 'No_High_limit'
    assert r0['lower_limit'] == '0'
    assert r0['upper_limit'] == 'NA'
    assert r0['result'] == 'pass'

    r1 = real_results[1]
    assert r1['sub_test'] == 'No_Low_Limit'
    assert r1['lower_limit'] == 'NA'
    assert r1['upper_limit'] == '8'
    assert r1['value'] == '11'

    pypudding.IP_reply_destroy(reply)
    del uut

if __name__ == '__main__':
    print('instantPudding version:' + pypudding.INSTANT_PUDDING_VERSION)

    gh_station = pypudding.IPGHStation()
    print('station number: ' + str(gh_station[pypudding.IP_STATION_NUMBER]))
    print('station line number: ' + str(gh_station[pypudding.IP_LINE_NUMBER]))
    print('station mac address: ' + str(gh_station[pypudding.IP_MAC]))
    print('station spider cap ip:' + str(gh_station[pypudding.IP_SPIDERCAB_IP]))
    del gh_station

    test_commit_run()
