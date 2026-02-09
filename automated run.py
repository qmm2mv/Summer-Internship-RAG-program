import logging
import os
import time
from main import main
from populate_database import main as populate_main


# Only log warnings
logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s")
#this is the list of folders that the program will run on.
folders=["Slovenia_original copy"]
#list of questions that each folder will be queried on
questions = [
    "Please provide the name of the analysed central bank",
    "Is there any mention of the central bank in the Constitution (A) Yes (B) No (C) Constitution not available",
    "What is the name of the primary legislation annualized?",
    "Which is the date of this primary legislation?",
    "What is the name of the secondary legislation analized?",
    "Which is the date of the secondary legislation?",
    "Which is the term of office of the President/Prime Minister of the Country?",
    "Term of office of the Governor/President (A) More than 8 years (B) 6 to 8 years (C) Equal to 5 years (D) Equal to 4 years (E) Less than 4 years or at the discretion of the appointer (No limits or not mentioned)",
    "Duration of the Term of office of the Governor/President (A) More than the Presidential/Prime Minister period (B) The period does not coincide (C) Same period as the executive branch (D) Less than executive branch or not specified in the law",
    "Governor/President reappointment option (A) Yes (B) No (C) Not mentioned",
    "Maximum term of reappointment of Governor/President (A) More than 2 terms or no limits (if the law clearly mention the possibility for reappointment) (B) 2 terms (C) 1 term (D) No reappointability (E) Not Mentioned",
    "Who appoints the Governor/President? (A) Shareholders / Governments of the Member States for Monetary Unions (B) The Central bank Board (C) The Central bank Board, with the approval of the Government (D) A council of the central bank Board, Executive branch, and Legislative branch / by the Legislative branch on proposal by the central bank Board (E) By the Legislative branch (F) By the Executive branch collectively (e.g. Council of Ministers) (G) By one or more members of executive branch",
    "Is double-veto arrangement required for the election of the Governor/President? (A) Double process (Executive/Legislative), or through the central bank Board if also appointed in a double process, or for longer or overlapped periods with respect to the executive branch (B) The executive branch directly or through the central bank Board, when this is directly appointed by the executive branch",
    "Provisions for the dismissal of the Governor/President (A) No provision for dismissal (B) Only for non-policy reasons (e.g., incapability, or violation of law) (C) At the discretion of the central bank Board (D) For policy reasons at the legislative branch's discretion (E) At the legislative branch's discretion (F) For policy reasons at the executive branch's discretion (G) At the executive branch's discretion",
    "May Governor/President hold other offices in the Government? (A) Prohibited by law (B) Not allowed unless authorised by the executive branch (C) No prohibition for holding another office (D) Not mentioned",
    "Are there specific requirements for becoming Governor/President? (A) Yes (B) No / Not mentioned",
    "Are professional skills a mandatory qualification for becoming the Governor/President? (A) Yes (B) No / Not mentioned",
    "Are education skills a mandatory qualification for becoming the Governor/President? (A) Yes (B) No / Not mentioned",
    "Is individual character of integrity a mandatory qualification for becoming Governor/President? (A) Yes (B) No / Not mentioned",
    "Does the Governor/President need to be a citizen of the Country to be appointed for the function? (A) Yes (B) No / Not mentioned",
    "Is there a retirement age for the Governor/President? (A) Yes (B) No / Not mentioned",
    "How many vice CEO/Governors are required by the legislation?",
    "Name of the main Board/Committee of the central bank",
    "Term of office of the rest of the Board (A) More than 8 years (B) 6 to 8 years (C) Equal to 5 years (D) Equal to 4 years (E) Less than 4 years or at the discretion of the appointer (No limits or not mentioned)",
    "Does the legislation require staggering terms for the appointment of Board members (The scheduling of terms of office so that all members of a body are not selected at the same time)? (A) Yes (B) No / Not mentioned",
    "Rest of the Board reappointment option (A) Yes (B) No (C) Not mentioned",
    "Maximum reappointment of the rest of the Board (A) More than 2 terms or no limits (if the law clearly mentions the possibility for reappointment) (B) 2 terms (C) 1 term (D) No reappointability (E) Not Mentioned",
    "Who appoints the rest of the Board? (A) Shareholders / Governments of the Member States for Monetary Unions (B) The Central bank Board (C) The Central bank Board, with the approval of the Government (D) A council of the central bank Board, the Executive branch, and the Legislative branch (E) By the Legislative branch (F) By the Executive branch collectively (e.g. Council of Ministers) (G) By one or more members of the executive branch",
    "Appointment and term of office rest of the Board? (A) More than the presidential/Prime Minister period, or for an undefined period (B) For the same period as the President of the Republic, with overlap (C) Double process for the same period (D) The executive and private sector appoint the majority of directors for the same period or less (E) The executive branch appoints the majority for the same period or less",
    "Are more than half of the policy board appointments made independently of the government? (A) Yes (B) No",
    "Is a double-veto arrangement required for the election of Board members? (A) Double process (Executive/Legislative), or through the central bank Board if also appointed in a double process, or for longer or overlapped periods with respect to the executive branch (B) The executive branch directly or through the central bank Board, when this is directly appointed by the executive branch",
    "Provisions for dismissal of the rest of the Board members (A) No provision for dismissal (B) Only for non-policy reasons (e.g., incapability, or violation of law) (C) At the discretion of the central bank Board (D) For policy reasons at the legislative branch's discretion (E) At the legislative branch's discretion (F) For policy reasons at the executive branch's discretion (G) At the executive branch's discretion",
    "Dismissal of Board members (A) Double process approved by the Senate or by a qualified majority, and for violations codified in legislation (B) By an independent Central bank Board (C) Double process with a simple majority, based on policy decisions or due to subjective reasons (D) By the executive branch or the subordinated Central bank Board due to legal reasons (E) By the executive branch or the subordinated Central bank Board due to policy or subjective reasons, or no legal provision (F) Not mentioned",
    "May the rest of the Board members hold other offices in government? (A) Prohibited by law (B) Not allowed unless authorised by the executive branch (C) No prohibition for holding another office (D) Not mentioned",
    "Are there specific requirements for becoming a Board member? (A) Yes (B) No / Not mentioned",
    "Are professional skills a mandatory qualification for becoming a Board member? (A) Yes (B) No / Not mentioned",
    "Are education skills a mandatory qualification for becoming a Board member? (A) Yes (B) No / Not mentioned",
    "Is individual character of integrity a mandatory qualification for becoming a Board member? (A) Yes (B) No / Not mentioned",
    "Does the Board member need to be a citizen of the Country to be appointed? (A) Yes (B) No / Not mentioned",
    "Is there a retirement age for the rest of the Board members? (A) Yes (B) No / Not mentioned",
    "Is the Governor/President the presiding officer of the Board? (A) Yes (B) No (C) Not mentioned",
    "Can external members be appointed as Board members? (A) Yes (B) No (C) Not mentioned",
    "No mandatory participation of government representatives in the central bank Board (A) Yes (B) No (C) Not mentioned",
    "Have (if present) government representative voting rights in the Board? (A) Yes (B) No (C) Not present",
    "How many government representatives are present on the Board?",
    "If not a member of the Board, can the Minister of Finance or their representative attend the meeting of the central bank? (A) No (B) Yes (C) Already present on the Board",
    "If the Minister of Finance, or its representative, can attend the meeting of the central bank, can he also give opinions (A) No (B) Yes (C) Already present on the Board or not allowed to participate in the meeting",
    "Are there any Ex Officio (different from government representatives) members on the Board? (A) Yes (B) No",
    "How many Ex Officio members are present on the Board?",
    "Does the legislation require the presence of a certain sectoral representative? (A) Yes (B) No, not required",
    "Does the legislation require the presence of a certain regional/national representative? (A) Yes (B) No, not required",
    "Have (if present) Ex Officio members voting rights in the Board? (A) Yes (B) No (C) Not present",
    "Number of members of the Board (Governor & Vice included)",
    "How many internal members are present on the Board?",
    "Number of voting members of the Board (Governor & Vice included)",
    "Are the majority of the members internal or external? (A) Internals (B) Externals",
    "Does the law specify a quorum for adopting decisions? (A) Yes (B) No",
    "Is there a majority principle for adopting Board decisions? (A) Yes (B) No (C) Not Mentioned",
    "Does the CEO/Governor have special voting rights? (A) Casting (Double) vote in case of parity (B) Veto (C) None (D) Not Mentioned",
    "Is the management of the central bank attributed to a sole person? (A) Yes (B) No (C) Not Mentioned",
    "Who is the person or the board in charge of the management of the central bank? (A) Governor/President (B) Chairman (if he is not the Governor/President) (C) General Manager (D) Board of Directors (E) Other (specify)",
    "Does the Board or a specific Committee fix the salary of the Governor? (A) Yes (B) No (C) Not Mentioned",
    "Who fixes the salary of the Governor?",
    "Does the Board or a specific Committee fix the salary of the other board members? (A) Yes (B) No (C) Not Mentioned",
    "Who fixes the salary of the other Board members?",
    "Who formulates monetary policy? (A) Bank alone (B) Bank participates, but has little influence (C) The Central bank only advises the government (D) The Central bank has no say (E) Not mentioned",
    "Is uniquely the Governor/President responsible for formulating monetary policy? (A) No (B) Yes",
    "Has the government (or Parliament) the right to give instructions? (A) No (B) Yes",
    "Which is the authority that has the right to give instructions? (A) Government (B) Parliament (C) Both (D) None",
    "Does the central bank have obligations to provide advice on economic policy to the government? (A) No (B) Yes",
    "Relation of the central bank with the Government (approval/consultation of the Members of the Parliament) (A) Independence (B) Consultation (C) Approval (D) Not mentioned",
    "Relation of the central bank with Parliament (A) Independence (B) Consultation (C) Approval (D) Not mentioned",
    "Does the central bank have the possibility for an appeal in case of an instruction? (A) Independence (B) Yes (C) No / Not mentioned",
    "Who has the final word in the resolution of conflict? (A) The bank, on issues clearly defined in the law as its objectives (B) Government, on policy issues not clearly defined as the central bank's goals or in case of conflict within the central bank (C) A council of the central bank, executive branch, and legislative branch (D) The legislature, on policy issues (E) The executive branch on policy issues, subject to due process and possible protest by the central bank (F) The executive branch has unconditional priority (G) Not mentioned",
    "The Central bank is given an active role in the formulation of the government's budget (A) The central bank is active (B) The central bank has no influence or is not mentioned",
    "Report the list of central bank objectives",
    "Does the central bank law stipulate the objectives of monetary policy (A) Yes (B) No",
    "Are the objectives clearly defined? (A) Yes (B) No",
    "Is there a clear prioritisation of objectives (A) Yes (B) No",
    "Are the objectives quantified (in the law or based on a document based on the law) (A) Yes (B) No",
    "Is past performance a ground for dismissal of a central bank governor? (A) No (B) Yes",
    "Price stability objective (A) Price stability is the major or only objective in the charter, and the central bank has the final word in case of conflict with other government objectives (B) Price stability is the only objective (C) Price stability is one goal, with other compatible objectives, such as a stable banking system (D) Price stability is one goal, with potentially conflicting objectives, such as full employment (E) No objectives stated in the central bank charter (F) Stated objectives do not include price stability",
    "Is the central bank adopting an Inflation Targeting Regime? (A) Yes (B) No (C) No information available",
    "When did the central bank adopt the Inflation Targeting Regime (if applicable)",
    "Is there a formal statement of the objective(s) of monetary policy, with an explicit prioritisation in case of multiple objectives? (A) No formal objective(s) (B) Multiple objective(s) without prioritization (C) One primary objective of multiple objectives with explicit priority",
    "Is Financial/Monetary Stability one of the primary goals? (A) Yes (B) No (C) Not Mentioned",
    "Is the central bank responsible for setting the policy rates? (A) Yes (B) No (C) Not Mentioned",
    "Central bank involvement in debt approval (A) Approves government debt (B) Legally required to provide an opinion on technical aspects (C) No involvement at all / Not Mentioned",
    "Is there no responsibility of the central bank for overseeing the central banking sector? (A) Yes (B) Banking supervision is not entrusted to the central bank alone (C) Banking supervision is entrusted to the central bank alone (D) Information not available for the analysed period",
    "Which is/are the authority/authorities responsible for overseeing the central banking sector?",
    "Which is/are the authority/authorities responsible for overseeing the insurance sector?",
    "Which is/are the authority/authorities responsible for overseeing the stock markets?",
    "Lending to Government (A) Not allowed (B) In the secondary market with restricted limits (C) In the secondary market with lax or without limits (D) In the primary market, with limits or approved by the central bank Board with a qualified majority (E) In the primary market without limits (F) Not mentioned",
    "Advances (limitation on nonsecuritized lending) (A) No advances permitted (B) Advances permitted, but with strict limits (e.g., up to 15 percent of government revenue) (C) Advances permitted, and the limits are loose (e.g., over 15 percent of government revenue) (D) No legal limits on lending or limits subject to negotiations with the government (E) Not mentioned",
    "Securitised lending (A) Not permitted (B) Permitted, but with strict limits (e.g., up to 15 percent of government revenue) (C) Permitted, and the limits are loose (e.g., over 15 percent of government revenue) (D) No legal limits on lending. Subject to negotiations with the government (E) Not mentioned",
    "Who decides financing conditions for the government (maturity, interest, amount) (A) No advances permitted (B) Determined by the market (C) Controlled by the central bank (D) Specified by the central bank charter (E) Agreed between the central bank and the executive (F) Decided by the executive branch alone",
    "Potential borrowers from the central bank (A) No advances permitted (B) Only the government (C) Government plus local governments (D) All of the above plus public enterprises (E) All of the above, and to the private sector, also if it is not mentioned otherwise",
    "Limits on central bank lending are defined (A) No advances permitted (B) As an absolute cash amount (C) As a percentage of Central bank capital or other liabilities (D) As a percentage of government revenues (E) As a percentage of government expenditure (F) Fixed by agreement between the central bank and a member of the Executive Branch or no limits on lending (G) Not Mentioned",
    "Maturity of loans (A) No advances permitted (B) Within 6 months (C) Within 1 year (D) More than 1 year (E) No mention of maturity in the law",
    "Interest rates on loans must be (A) No advances permitted (B) Must be at market rate (C) On loans to the government cannot be lower than a certain floor (D) Interest rate on Central bank loans can not exceed a certain ceiling (E) No explicit legal provisions regarding interest rate in Central bank loans (F) No interest rate charged on the government's borrowing from the central bank (G) At the discretion of the central bank or agreed upon between the Bank and the Government (H) No such mention in the law",
    "The Central bank is prohibited from buying or selling government securities in the primary market (A) Yes (B) No such prohibition in the legislation",
    "The Statute describes precisely the provisions relating to the payment, by the State or Shareholders, of the initial capital (A) Yes (B) No",
    "The Statute quantify precisely the authorised capital of the central bank (A) Yes (B) No",
    "Financial autonomy (A) The government should maintain central capital integrity (B) The government is legally allowed to capitalise the central bank (C) The law does not allow the government to capitalise the central bank (D) The Central bank conducts quasi-fiscal operations (E) Not Mentioned",
    "The State has the power to impose, unilaterally, measures to reduce the capital of the central bank (A) No / Not mentioned (B) Yes",
    "Are there legal arrangements allowing for an automatic capital contribution upon the request by the central bank (automatic recapitalisation)? (A) Yes (B) No / Not mentioned",
    "Are recapitalisations on request of the central bank subject to approval by the executive government or parliament? (A) No (B) Yes (C) Not mentioned",
    "How are managed, from a legislative point of view, transfers of money from the Treasury to the central bank? (A) The decision is based on technical criteria (B) The transfer requires approval by the Treasury (C) The transfer requires an act of the legislature (D) Not mentioned",
    "Ownership of the central bank (A) Public (B) Private (C) Public & Private (D) Not available",
    "Percentage of Government ownership",
    "Percentage owned by other shareholders",
    "Is there any requirement for the allocation of the central bank profits (A) Yes (B) No (C) Not Mentioned",
    "The allocation of the net profits of the central bank is (A) Prescribed by the Statute / Central bank Charter (B) Left to the discretion of the central bank (C) A kind of negotiation between the government and the central bank (D) Left to the discretion of the Government",
    "The Central bank has the power to create, in a completely independent manner, financial provisions and capital reserves (A) Yes (B) No (C) No mention of profit allocation",
    "How is the allocation to the general reserve fund of a percentage of the profits handled by the central bank (A) The decision is just on objective criteria established precisely by the Statute (B) The decision is left to the discretion of the central bank (C) The decision is made by the deciding body of the central bank in consultation with the Government (D) Other options (Specify) (E) No mention of profit allocation",
    "Does the legislation require a 'Graduated sharing approach' for the allocation of profits to the general reserve? (A) Yes (B) No (C) No mention of profit allocation",
    "Does the legislation require a 'Fully rules-based sharing approach' for the allocation of profits to the general reserve? (A) Yes (B) No (C) No mention of profit allocation",
    "Does the law specify that a part of the profits has to be allocated to a general reserve? (A) Yes (B) No (C) No mention of profit allocation",
    "Is the percentage of profits to be allocated to the general reserve determined? (A) Yes (B) No (C) No mention of profit allocation",
    "In the allocation of profits, does the amount allocated to the general reserve have precedence? (A) Yes (B) No (C) No mention of profit allocation",
    "Does the legislation set a maximum amount for the general reserve? (A) Yes (B) No (C) No mention of profit allocation",
    "If the law specifies that a part of the profits has to be allocated to a general reserve, what is the maximum amount that this reserve can reach?",
    "Is there a fixed amount of money that has to be distributed to the State, no matter what the amount of profits? (A) No (B) Yes (C) No mention of profit allocation",
    "Specify the fixed amount of money that has to be distributed to the State, no matter what the amount of profits",
    "Can the State or the Shareholders receive partial payments before the end of the fiscal year, based on an estimate for that year? (A) No / Not mentioned (B) Yes (C) No mention of profit allocation",
    "Also unrealised profits are included in the calculation of distributable profits at the end exercise. (A) No / Not mentioned (B) Yes (C) No mention of profit allocation",
    "Central bank reporting (A) Reports to the executive branch and informs at least annually to Congress (B) Reports to the executive once a year and submits an annual report to Congress (C) Annual report to the executive. Informs the executive branch whenever fundamental disequilibria emerge, or reports through the media without specific periodicity (D) Issues annual report at a specific time (E) Distributes an annual report without establishing a particular period of time (F) Not Mentioned",
    "Is the central bank subject to monitoring by Parliament (is there a requirement, apart from an annual report, to report to Parliament and/or explain policy actions in Parliament) (A) No (B) Yes (C) Not Mentioned",
    "Central bank financial statements (A) Discloses detailed financial statements at least once a year with a certification from an independent auditor (B) Discloses consolidated financial statements at least once a year with the seal of the Banking Superintendent or other public sector authority (C) Discloses financial statements at least once a year, certified by an internal (D) Publishes partial financial statements (E) Does not publish financial statements, or the law authorises the central bank to deviate from international accounting standards (F) Not Mentioned",
    "The Central bank has the exclusive right to determine and approve its annual budget (A) Yes (B) Ex-post approval by the government (C) No",
    "The adoption of the annual budget of the central bank belongs exclusively to its decision-making bodies (A) Yes (B) No",
    "The accounts of the central bank are subject to the control of a state agency of Auditing. (A) No (B) No, but the external audit agency is appointed by the government (C) Yes",
    "Who is in charge of the auditing of the annual report or the financial statement of the central bank? (A) Internal independent auditors (B) External independent auditors (C) Government’s General Auditor (D) Others (Specify) (E) Not mentioned",
    "Can the central bank law be changed by a simple majority in Parliament? (A) No (B) Yes",
    "Is there a mention concerning the minutes of meetings of the governing board of the central bank in the Central Bank Charter? (A) Yes (B) No",
    "Does the law specify if the minutes of the meeting have to be published? (A) Yes (B) No",
    "Is the central bank LOLR in the country? (A) Yes (B) No / Not mentioned",
    "Name of special Board(s)/Committee(s) of the central bank",
    "Number of special Board(s)/Committee(s) of the central bank",
    "Functions of special Board(s)/Committee(s) of the central bank",
    "Number of members of special Board(s)/Committee(s) of the central bank",
    "Is the Governor/President the presiding officer of this / all these Board(s)?",
    "Which authority appoints the Governor/President?"
]



def auto_run():
    # Default arguments for the main function
    default_args = {
        "num_chunks": 2,
        "model": "phi3:mini",
        "max_context": 2500,
        "source_filter": None,
        "show_chunks": False,
    }

    for folder in folders:
        print(f"Starting processing for folder: {folder}")
        #default argument for resetting the database
        default_populate_args = [
            "--reset",
            "--chunk-size", "900",
            "--chunk-overlap", "50",
            "--splitter-type", "token",
            "--folder-filter", folder
        ]
        try:
            logging.info(f"Populating database for folder: {folder}")
            populate_main(cli_args=default_populate_args)
            logging.info(f"Database populated successfully for folder: {folder}")
        except Exception as e:
            logging.error(f"Failed to populate database for folder {folder}: {e}")
            continue  # Skip to the next folder if population fails

        # Process all questions for the current folder
        for i, base_query in enumerate(questions, 1):
            try:
                # Modify the query to include the country name
                query = f"{base_query.replace('?', ' of the ' + folder + ' central bank?')}"
                # Set output file name to country.txt
                output_file = f"{folder}.txt"
                # Construct the list of arguments for each query
                query_args = [
                    "--query_text", query,
                    "--num_chunks", str(default_args["num_chunks"]),
                    "--model", default_args["model"],
                    "--max_context", str(default_args["max_context"]),
                ]
                # calling main
                result = main(cli_args=query_args)

                # writing the response on a new line in the file
                logging.info("Writing response to output file")
                with open(output_file, "a", encoding="utf-8") as f:
                    f.write(f"Question {i}:\n{query}\n\nResponse: {result['text']}\n")
                    f.write("\nSources:\n")
                    for j, source in enumerate(result['sources'], 1):
                        # Extract filename from source path
                        source_name = os.path.basename(source['source']) if source['source'] != "Unknown" else "Unknown"
                        f.write(f"{j}. {source_name} (Page {source['page']})\n")
                    f.write("\n")
                print(f"Completed question {i} for folder: {folder}")
            except Exception as e:
                logging.error(f"Error processing question {i} for folder {folder}: {e}")
                continue  # Continue with the next question

        logging.info(f"Finished processing all {len(questions)} questions for folder: {folder}")

if __name__ == "__main__":
    start_time = time.time()
    try:
        auto_run()
        print(f"\n⏱️ Total execution time for all queries: {time.time() - start_time:.2f} seconds")
    except Exception as e:
        logging.error(f"Error in automated run: {e}")
        print(f"Error in automated run: {e}")
