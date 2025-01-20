from openai_client import OpenAIAssistant

PROMPT_CLEANING_AUDIO_TEXT="""Please clean up the following audio text by correcting spelling, grammar, and punctuation errors:
Return only the cleaned-up audio text.
For example:
Input:Early Voting Starts September 20thl Prepared & Paid for by Natalie for House 23 W. Central Entrance#192, Duluth, MN 55811 | Early Voting Starts September 20thl Prepared & Paid for by Natalie for House 23 W. Central Entrance#192, Duluth, MN 55811 | Early Voting Starts September 20thl Prepared & Paid for by Natalie for House 23 W. Central Entrance#192, Duluth, MN 55811
Output:Early voting starts September 20th! Prepared and paid for by Natalie for House, 23 W. Central Entrance #192, Duluth, MN 55811.
"""

PROMPT_CLEANING_OCR_TEXT="""
Please clean up the following  video frame OCR text by correcting spelling, grammar, and punctuation errors:
Return only the cleaned-up video frame OCR text.
Input:PHD FOR BVHARRIS FUR PRESHDENT OF THE UN VT | PHD FOR BV HARRIS FUR PRESHDEHT OF THE UN} NT | OF PHD FOR BVHARRIS FUR PRESHDELT THE 0 9
Output:Paid for by BV Harris for President of the United Nations.
"""

PROMPT_FINDING_MAIN_TAGS="""
Preclusion Tag:
If the ad is political but unrelated to US Elections, tag with #Non-US_Election_Ad.

Type One Tags (Election Type) – Level of Candidate/Measure:
#Federal_Elections:
Tag if the ad is promoting a federal candidate (e.g., U.S. Senate, House of Representatives, Presidency). This tag is applied regardless of funding source.
Example: "Vote for Joe Biden for President" or "Support Jack Jones for U.S. Senate".
#State_and_Local_Elections:
Tag if the ad is focused on state or local candidates or issues (e.g., state governor, local city council, school board elections, state ballot initiatives, etc.).
Example: "Support Jane Doe for Governor" or "Vote Yes on Proposition 23".
Restrictions: Local ads are not allowed in certain states like Idaho, Nevada, New Jersey, Washington. Apply appropriate restrictions if applicable.

Type Two Tags (Sponsor Type) – Funding Source Based on OCR data:
#Paid_by_Candidate_Campaign:
Tag if the ad is funded by the candidate or their campaign committee. This includes both positive and negative ads about an opponent that are funded by the candidate’s campaign.
Example: "Paid for by John Smith for Senate Committee".
#Paid_by_Political_Party_Third_Party-PAC:
Tag if the ad is funded by a political party, Super PAC, or any third-party organization (not directly funded by the candidate's campaign).
Example: "Paid for by the Republican National Committee" or "Paid for by the Democratic Party PAC".
Type Three Tags (Party Type) – Political Party Affiliation:
#Democrat_Party:
Tag if the ad is promoting Democratic Party candidates, issues, or policies.
Example: "Paid for by the Democratic National Committee" or "Vote for Kamala Harris, Democrat".
#Republican_Party:
Tag if the ad is promoting Republican Party candidates, issues, or policies.
Example: "Paid for by the Republican National Committee" or "Vote for Ron DeSantis, Republican".
#Third_Party_or_Non_Partisan:
Tag if the ad is promoting third-party, independent, or non-partisan candidates/issues.
Example: "Paid for by the Green Party" or "Vote for Gary Johnson, Libertarian".
Note: If the party affiliation is not explicitly mentioned in the text, infer the party based on candidate names or external data sources such as Ballotpedia or other relevant databases.

Additional Context for Improved Accuracy:
Assign only one tag from each of Type One, Type Two, and Type Three. If unsure, do not assign.
Contextual Inference for Party Affiliation:
If a candidate's name is recognized in the audio or OCR text (e.g., Kamala Harris, Ron DeSantis, etc.), infer their party affiliation based on well-known political associations.
If the affiliation is unclear, use external data sources such as Ballotpedia to identify the correct party.
OCR Text Analysis:
Use the OCR data to cross-check mentions of party names (e.g., “Republican Party”, “Democratic Party”, etc.) or political figures known to belong to those parties.
If OCR mentions “Super PAC”, “Republican National Committee”, or “Democratic National Committee”, tag the funding source with #Paid_by_Political_Party_Third_Party-PAC.
Ambiguity Handling:
In cases where the content is ambiguous or does not provide enough detail, avoid tagging.

Output Format
Format response as a Python list.

For example:
Input: Audio Text: Here are a few things I believe. Middle-class families, like the one I grew up in, want common-sense solutions. You want lower prices and lower taxes. I believe you want to not just get by, but to get ahead. We must create an opportunity economy where everyone has a chance to get a car  Top Frame OCR: Harris | Harris | Harris  Bottom Frame OCR: Walz, Kamala Harris, and I approve this message. Approved by Kamala Harris. Paid for by Harris for President.
Output: ["Democrat_Party"," Federal_Elections"," Paid_by_Candidate_Campaign"]
"""

PROMPT_FINDING_CONTENT_TAGS="""
Carefully read the entire transcription, considering the overall context and messaging strategy & give the appropriate tag to provided content.

#Social_Security
For any reference to the US Social Security program, including targeting seniors or attack ads against opponents for allegedly threatening reductions in retirement payments.
#Environmental_Politics
For ads discussing climate change, energy policies (e.g., fossil fuels), or CO2 emissions. Includes messaging on both sides of the climate debate.
#Criminal_Justice
For content about crime, prisons, bail reform, sentencing, or crime rates. Include additional tags (e.g., drug policy or immigration) if discussed alongside.
#Security_and_Foreign_Policy
For mentions of the Ukraine War, Israel/Hamas conflict, or US military interventions globally.
#Sex-Gender-LGBTQ_Issues
For issues related to gender, sexual orientation, trans rights, or trans-related medical procedures.
#Immigration
For discussions about the US/Mexico border, illegal immigration, or policies like "building a wall."
#Abortion_and_Reproductive_Health
For ads referencing abortion, Roe v. Wade, or pro-choice/pro-life arguments.
#Gun_Regulation
For mentions of gun rights, the Second Amendment, or gun control. Imagery of non-violent gun usage (e.g., hunting) is acceptable but avoid ads showing violence.
#Healthcare_and_Prescription_Drugs
For universal healthcare advocacy or high prescription drug cost issues.
#Illegal_Drug_Policy
For discussions of illegal drug use, Fentanyl imports, overdose deaths, or legalizing drugs like marijuana.
#Racial_Justice
For references to race-related policies, affirmative action, or racial equality.

Additional Tags
#DAA_Icon_Confirmed
For ads displaying the DAA icon, confirming compliance with legal ad buyer transparency requirements.
#Attack_Ads
For ads portraying a candidate negatively and not paid for by the featured candidate/campaign. Ad criticizes opponents, their policies, or contrasts the candidate's position with the opponent's, even indirectly.

Special State-Level Tags
For ads mentioning political candidates/issues in states requiring additional registration:
#California, #New_Jersey, #New_York, #Virginia, #Seattle


Guidelines for Applying Tags
Audio & OCR Input: Analyze both audio transcription and text from the last 2 seconds of video frames.
Accuracy: Apply tags only if the content is clear and relevant to the guidelines. Do not tag vague, ambiguous, or purely descriptive ads.
External Data: Use external data (e.g., party affiliations, candidate information) when inferring context, such as political party association.
Multiple Tags: Ads often qualify for multiple tags (e.g., #Illegal_Drug_Policy + #Criminal_Justice for drugs and crime).
Do not modify or create new tags.
Include a topic if it's a significant focus or clearly implied, even if not explicitly stated.

Output Format
Format response as a Python list.

For example:
Input: Audio Text: It's an unthinkable trauma when a woman is raped and becomes pregnant. As a sexual assault counselor, I've seen it too many times. But Sam Brown has spent the last decade pushing to ban abortion without any exception for rape or incest. He even supported the Texas ban, one of the harshest in the country  Top Frame OCR: This is top frame OCR: ||  Bottom Frame OCR: Paid for by Friends of Jacky Rosen, approved by Jacky Rosen.
Output: ["Social_Security","Healthcare_and_Prescription_Drugs","Immigration"]
"""


def getTagsForUnprocessedContent(audio_ocr_text:str, top_frame_ocr_text:str, bottom_frame_ocr_text:str):
    """
    This function will take the audio OCR text, top frame OCR text and bottom frame OCR text as input and return the tags for the content as output.
    """
    assistant = OpenAIAssistant()
    cleaned_audio_text = assistant.gpt_4_min_response(f"{PROMPT_CLEANING_AUDIO_TEXT} \n Audio Text: {audio_ocr_text}")
    cleaned_top_frame_ocr_text = assistant.gpt_4_image_response(f"{PROMPT_CLEANING_OCR_TEXT} \n Top Frame OCR test list: {top_frame_ocr_text}")
    cleaned_bottom_frame_ocr_text = assistant.gpt_4_image_response(f"{PROMPT_CLEANING_OCR_TEXT} \n Bottom Frame OCR test list: {bottom_frame_ocr_text}")
    
    tags = assistant.gpt_4_min_response(f"{PROMPT_FINDING_CONTENT_TAGS} \n Audio Text: {cleaned_audio_text} \n Top Frame OCR: {cleaned_top_frame_ocr_text} \n Bottom Frame OCR: {cleaned_bottom_frame_ocr_text}")
    
    return tags

    
     