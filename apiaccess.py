import requests
import sys
import json


infermedica_url = 'https://api.infermedica.com/v3/{}'


def _remote_headers(auth_string, case_id, language_model=None):
    print("Sanchyan Checking _remote_headers in apiacess.py >>>")
    print("auth_string >>> ", auth_string)
    print("case_id >>> ", case_id)
    auth_string = '43446992:fc94728c49d650cf38434eed81706d17'
    headers = {
        'Content-Type': 'application/json',
        'Dev-Mode': 'true',  # please turn this off when your app goes live
        'Interview-Id': case_id,
        'App-Id': '43446992',
        'App-Key': 'fc94728c49d650cf38434eed81706d17'}
    if language_model:
        headers['Model'] = language_model
    return headers


def call_endpoint(endpoint, auth_string, params, request_spec, case_id,
                  language_model=None):
    print("Sanchyan Checking in call_endpoint in apiaccess.py")
    print("endpoint >> ",endpoint)
    #endpoint = "parse"
    print("auth_string >> ",auth_string)
    print("params >> ",params)
    #params = {"App-Id" : "43446992", "App-Key" : "fc94728c49d650cf38434eed81706d17", "Content-Type" : "application/json"}
    """request_spec = {
    "age" : {"value": 30},
    "sex" : "male",
    "evidence" : "nothing",
    "text": "I feel smoach pain but no couoghing today"}
    """
    print("params >> ",params)
    
    #print("request_speresp 1 >>> ",rc >> ",request_spec)
    #print("case_id >> ",case_id)
    if auth_string and ':' in auth_string:
        url = infermedica_url.format(endpoint)
        headers = _remote_headers(auth_string, case_id, language_model)
    else:
        raise IOError('need App-Id:App-Key auth string')
    if language_model:
        # name of a model that designates a language and possibly a
        # non-standard knowledge base e.g. infermedica-es
        # (the default model is infermedica-en)
        # extract the language code complaintsif model name provided
        if '-' in language_model:
            lang_code = language_model.split('-')[-1]
        else:
            lang_code = language_model
        headers['Language'] = lang_code
    print("request_spec >>> ",json.dumps(request_spec))
    if request_spec:
        print("Heaaders >>>> ",headers)
        print("url >>>> ",url)
        print("params >>>> ",params)
        print("json >>>> ",request_spec)
        print("headers >>>> ",headers)
        resp = requests.post(
            url,
            params=params,
            json=request_spec,
            headers=headers)
        print("resp 1 >>> ",resp)
    else:
        print("Sanchyan need to check here >> ")
        print("url >>> ",url)
        print("params >>> ",params)
        print("headers >>> ",headers)
        #sys.exit(0)
        resp = requests.get(
            url,
            params=params,
            headers=headers)
        print("resp 2 >>> ",resp)
     
    resp.raise_for_status()
    return resp.json()


def call_diagnosis(evidence, age, sex, case_id, auth_string, no_groups=True,
                   language_model=None):
    print("Sanchyan Checking call_diagnosis in apiacess.py >>>")
    """Call the /diagnosis endpoint.
    Input: evidence and patient basic data (age and sex).
    Output:
    1. next question to be answered by the patient (differential diagnosis);
    2. current outlook (list of diagnoses with probability estimates);
    3. "stop now" flag -- if the diagnostic engine recommends to stop asking
       questions now and present
    the current outlook as final results.

    Use no_groups to turn off group questions (they may be both single-choice
    questions and multiple questions gathered together under one subtitle; it's
    hard to handle such questions in voice-only chatbot).
    """
    request_spec = {
        'age': age,
        'sex': sex,
        'evidence': evidence,
        'extras': {
            # voice/chat apps usually can't handle group questions well
            'disable_groups': no_groups
        }
    }
    print("Sanchyan Checking before calling call_endpoint in apiacess.py >>>")
    print("call_endpoint tracking error 4 >>> ") 
    return call_endpoint('diagnosis', auth_string, None, request_spec, case_id,
                         language_model)


def call_triage(evidence, age, sex, case_id, auth_string, language_model=None):
    print("Sanchyan Checking   call_triage in apiacess.py >>>")
    """Call the /triage endpoint.
    Input: evidence and patient basic data (age and sex).
    Output:
    1. next question to be answered by the patient (differential diagnosis);
    2. current outlook (list of diagnoses with probability estimates);
    3. "stop now" flag -- if the diagnostic engine recommends to stop asking
       questions now and present
    the current outlook as final results.

    Use no_groups to turn off group questions (they may be both single-choice
    questions and multiple questions gathered together under one subtitle; it's
    hard to handle such questions in voice-only chatbot).
    """
    request_spec = {
        'age': age,
        'sex': sex,
        'evidence': evidence
    }
    print("call_endpoint tracking error 5 >>> ") 
    return call_endpoint('triage', auth_string, None, request_spec, case_id,
                         language_model)


def call_parse(age, sex, text, auth_string, case_id, context=(),
               conc_types=('symptom', 'risk_factor',), language_model=None):
    print("Sanchyan Checking   call_parse in apiacess.py >>>")
    print("age >>> ", age)
    print("sex >>> ", sex)
    print("text >>> ", text)
    print("auth_string >>> ", auth_string)
    print("case_id >>> ", case_id)
    
    """Process the user message (text) via Infermedica NLP API (/parse) to 
    capture observations mentioned there. Return a list of dicts, each of them
    representing one mention. A mention refers to one concept (e.g. abdominal
    pain), its status/modality (present/absent/unknown) + some additional
    details. Providing context of previously understood observations may help
    make sense of partial information in some cases. Context should be a list
    of strings, each string being an id of a present observation reported so
    far, in the order of reporting. 
    See https://developer.infermedica.com/docs/nlp ("contextual clues").
    """
    request_spec = {
       'age': age,
       'sex': sex,
       'text': text,
       'context': list(context),
       'include_tokens': True,
       'concept_types': conc_types,
       }
    #print("request_spec >> ",request_spec)
    #sys.exit(0)
    print("call_endpoint tracking error 1 >>> ")   
    return call_endpoint('parse', auth_string, None, request_spec, case_id,
                         language_model=language_model)


def get_observation_names(age, auth_string, case_id, language_model=None):
    print("Sanchyan Checking   get_observation_names in apiacess.py >>>")
    print("age >> ", age)
    print("auth_string >> ", auth_string)
    print("case_id >> ", case_id)
    """Call /symptoms and /risk_factors to obtain full lists of all symptoms
    and risk factors along with their metadata. Those metadata include names
    and this is what we're after. Observations may contain both symptoms and
    risk factors. Their ids indicate concept type (symptoms are prefixed s_,
    risk factors -- p_)."""
    obs_structs = []
    print("call_endpoint tracking error 2 >>> ") 
    obs_structs.extend(
        call_endpoint('risk_factors', auth_string,
                      {'age.value': age['value'], 'age.unit': age['unit']},
                      None, case_id=case_id, language_model=language_model))
    


    print("call_endpoint tracking error 3 >>> ") 
    obs_structs.extend(
        call_endpoint('symptoms', auth_string,
                      {'age.value': age['value'], 'age.unit': age['unit']},
                      None, case_id=case_id, language_model=language_model))
    
    #test = {struct['id']: struct['name'] for struct in obs_structs}
    #print("test >>>> ",test)
    #sys.exit(0)
    return {struct['id']: struct['name'] for struct in obs_structs}


def name_evidence(evidence, naming):
    print("Sanchyan Checking   name_evidence in apiacess.py >>>")
    """Add "name" field to each piece of evidence."""
    for piece in evidence:
        piece['name'] = naming[piece['id']]


def mentions_to_evidence(mentions):
    print("Sanchyan Checking   mentions_to_evidence in apiacess.py >>>")
    """Convert mentions (from /parse endpoint) to evidence structure as
    expected by the /diagnosis endpoint.
    """
    return [{'id': m['id'], 'choice_id': m['choice_id'], 'source': 'initial'}
            for m in mentions]


def question_answer_to_evidence(question_struct_item, observation_value):
    print("Sanchyan Checking   question_answer_to_evidence in apiacess.py >>>")
    print("question_struct_item >> ", question_struct_item)
    """Return new evidence obtained via abswering the one item contained in a
    question with the given observation value (status)."""
    return [{'id': question_struct_item['id'],
             'choice_id': observation_value}]
