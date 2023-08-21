import requests
import pandas as pd

def get_trials(search_term):
    base_url = "https://clinicaltrials.gov/api/query/study_fields"
    params = {
        "expr": search_term,
        "fields": "NCTId,BriefTitle,OfficialTitle,BriefSummary,DetailedDescription,Condition,InterventionType,InterventionName,InterventionArmGroupLabel,InterventionDescription,Phase,StudyType,EnrollmentCount,PrimaryOutcomeMeasure,SecondaryOutcomeMeasure,EligibilityCriteria,Gender,MinimumAge,MaximumAge,HealthyVolunteers",
        "min_rnk": 1,
        "max_rnk": 100, #number of pulls 
        "fmt": "json"
    }
    
    #"fields": "NCTId,BriefTitle,OfficialTitle,BriefSummary,DetailedDescription,Condition,InterventionType,InterventionName,InterventionArmGroupLabel,InterventionDescription,Phase,StudyType,EnrollmentCount,PrimaryOutcomeMeasure,SecondaryOutcomeMeasure,EligibilityCriteria,Gender,MinimumAge,MaximumAge,HealthyVolunteers,LocationCountry,
    #bad fields: LocationCountry, StudyStartDate,PrimaryCompletionDate,StudyFirstPostDate,LastUpdatePostDate",

    response = requests.get(base_url, params=params)
    data = response.json()
    return pd.DataFrame(data["StudyFieldsResponse"]["StudyFields"])





