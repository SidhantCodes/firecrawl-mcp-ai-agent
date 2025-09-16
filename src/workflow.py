# import os
# from typing import Dict, Any
# from langgraph.graph import StateGraph, END
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.messages import HumanMessage, SystemMessage
# from .models import ResearchState, CompanyAnalysis, CompanyInfo
# from .firecrawl_service import FirecrawlService
# from .prompts import DeveloperToolsPrompts


# class Workflow:
#     def __init__(self):
#         self.firecrawl = FirecrawlService()
#         self.llm = ChatGoogleGenerativeAI(
#             model="gemini-1.5-flash", # Note: Changed to a more recent model, you can change it back
#             temperature=0.1,
#             google_api_key=os.getenv("GOOGLE_API_KEY")
#         )
#         self.prompts = DeveloperToolsPrompts()
#         self.workflow = self._build_workflow()

#     def _build_workflow(self):
#         graph = StateGraph(ResearchState)
#         graph.add_node("extract_tools", self._extract_tools_setup)
#         graph.add_node("research", self._research_step)
#         graph.add_node("analyze", self._analyze_step)
#         graph.set_entry_point("extract_tools")

#         graph.add_edge("extract_tools", "research")
#         graph.add_edge("research", "analyze")
#         graph.add_edge("analyze", END)

#         return graph.compile()

#     def _extract_tools_setup(self, state: ResearchState) -> Dict[str, Any]:
#         print(f"🔍 Finding articles about: {state.query}")
#         article_query = f"{state.query} tools comparision best alternative"
#         search_results = self.firecrawl.search_companies(article_query, num_results=3)

#         all_content = ""
        
#         # This part is correct, using search_results.web
#         if search_results and search_results.web:
#             for result in search_results.web:
#                 url = result.url

#                 scrapped = self.firecrawl.scrape_company_pages(url)
#                 if scrapped:
#                     all_content += scrapped.markdown[:1500] + "\n\n"
        
#         messages = [
#             SystemMessage(content=self.prompts.TOOL_ANALYSIS_SYSTEM),
#             HumanMessage(content=self.prompts.tool_extraction_user(state.query, all_content))
#         ]
        
#         try:
#             res = self.llm.invoke(messages)
#             tool_names = [
#                 name.strip()
#                 for name in res.content.strip().split("\n")
#                 if name.strip()
#             ]
#             return {"extracted_tools": tool_names}
        
#         except Exception as e:
#             return {"error": e}
        
#     def _analyze_company_content(self, company_name: str, content: str) -> CompanyAnalysis:
#         structured_llm = self.llm.with_structured_output(CompanyAnalysis)
        
#         messages = [
#             SystemMessage(content=self.prompts.TOOL_ANALYSIS_SYSTEM),
#             HumanMessage(content=self.prompts.tool_analysis_user(company_name, content))
#         ]

#         try:
#             analysis = structured_llm.invoke(messages)
#             return analysis
        
#         except Exception as e:
#             print(f"Error analyzing {company_name}: {e}")
#             return CompanyAnalysis(
#                 pricing_model="Unknown",
#                 is_open_source=None,
#                 tech_stack=[],
#                 description="Failed to analyze content.",
#                 api_available=None,
#                 language_support=[],
#                 integration_capabilities=[]
#             )
    
#     def _research_step(self, state: ResearchState) -> Dict[str, Any]:
#         extracted_tools = getattr(state, "extracted_tools", [])

#         if not extracted_tools:
#             print("⚠️ No extracted tools found, falling back to direct search")
#             search_results = self.firecrawl.search_companies(state.query, num_results=4)
#             # This part is correct, using search_results.web
#             tool_names = [
#                 result.title for result in search_results.web if result.title
#             ]
#         else:
#             tool_names = extracted_tools[:4]
        
#         print(f"🔬 Researching specific tools: {', '.join(tool_names)}")

#         companies = []

#         for tool_name in tool_names:
#             tool_search_results = self.firecrawl.search_companies(tool_name + " official site", num_results=1)

#             # --- KEY CHANGE AREA ---
#             # Updated to use .web attribute, which is the correct way based on the latest API.
#             # Also added a check to ensure the list is not empty before accessing.
#             if tool_search_results and tool_search_results.web:
#                 result = tool_search_results.web[0]
#                 # Accessing properties directly (e.g., result.url) is cleaner
#                 url = result.url

#                 company = CompanyInfo(
#                     name=tool_name,
#                     # Using the markdown from the search result as an initial description
#                     description=result.markdown,
#                     website=url,
#                     tech_stack=[],
#                     competitors=[]
#                 )

#                 scrapped = self.firecrawl.scrape_company_pages(url)
#                 if scrapped:
#                     content = scrapped.markdown
#                     analysis = self._analyze_company_content(company.name, content)
                    
#                     if analysis:
#                         company.pricing_model = analysis.pricing_model
#                         company.is_open_source = analysis.is_open_source
#                         company.tech_stack = analysis.tech_stack 
#                         company.description = analysis.description
#                         company.api_available = analysis.api_available
#                         company.language_support = analysis.language_support
#                         company.integration_capabilities = analysis.integration_capabilities
                
#                 companies.append(company)
#             # --- END OF CHANGE AREA ---
            
#         return {"companies": companies}
    
#     def _analyze_step(self, state: ResearchState) -> Dict[str, Any]:
#         print("✨ Generating recommendations")

#         company_data = ", ".join([
#             company.json() for company in state.companies
#         ])

#         messages = [
#             SystemMessage(content=self.prompts.RECOMMENDATIONS_SYSTEM),
#             HumanMessage(content=self.prompts.recommendations_user(state.query, company_data))
#         ]

#         response = self.llm.invoke(messages)

#         return {"analysis": response.content}
    

#     def run(self, query: str) -> ResearchState:
#         initial_state = ResearchState(query=query)
#         final_state = self.workflow.invoke(initial_state)
#         return ResearchState(**final_state)

import os
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
# Assuming models.py and prompts.py are in the same directory (e.g., 'src')
from .models import ResearchState, CompanyAnalysis, CompanyInfo
from .firecrawl_service import FirecrawlService
from .prompts import DeveloperToolsPrompts


class Workflow:
    def __init__(self):
        self.firecrawl = FirecrawlService()
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.1,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        self.prompts = DeveloperToolsPrompts()
        self.workflow = self._build_workflow()

    def _build_workflow(self):
        graph = StateGraph(ResearchState)
        graph.add_node("extract_tools", self._extract_tools_setup)
        graph.add_node("research", self._research_step)
        graph.add_node("analyze", self._analyze_step)
        graph.set_entry_point("extract_tools")

        graph.add_edge("extract_tools", "research")
        graph.add_edge("research", "analyze")
        graph.add_edge("analyze", END)

        return graph.compile()

    def _extract_tools_setup(self, state: ResearchState) -> Dict[str, Any]:
        print(f"🔍 Finding articles about: {state.query}")
        article_query = f"{state.query} tools comparision best alternative"
        search_results = self.firecrawl.search_companies(article_query, num_results=3)

        all_content = ""
        
        if search_results and search_results.web:
            for result in search_results.web:
                url = result.url

                scrapped = self.firecrawl.scrape_company_pages(url)
                if scrapped and scrapped.markdown:
                    all_content += scrapped.markdown[:1500] + "\n\n"
        
        messages = [
            SystemMessage(content=self.prompts.TOOL_ANALYSIS_SYSTEM),
            HumanMessage(content=self.prompts.tool_extraction_user(state.query, all_content))
        ]
        
        try:
            res = self.llm.invoke(messages)
            tool_names = [
                name.strip()
                for name in res.content.strip().split("\n")
                if name.strip()
            ]
            return {"extracted_tools": tool_names}
        
        except Exception as e:
            return {"error": e}
        
    def _analyze_company_content(self, company_name: str, content: str) -> CompanyAnalysis:
        structured_llm = self.llm.with_structured_output(CompanyAnalysis)
        
        messages = [
            SystemMessage(content=self.prompts.TOOL_ANALYSIS_SYSTEM),
            HumanMessage(content=self.prompts.tool_analysis_user(company_name, content))
        ]

        try:
            analysis = structured_llm.invoke(messages)
            return analysis
        
        except Exception as e:
            print(f"Error analyzing {company_name}: {e}")
            return CompanyAnalysis(
                pricing_model="Unknown",
                is_open_source=None,
                tech_stack=[],
                description="Failed to analyze content.",
                api_available=None,
                language_support=[],
                integration_capabilities=[]
            )
    
    def _research_step(self, state: ResearchState) -> Dict[str, Any]:
        extracted_tools = getattr(state, "extracted_tools", [])

        if not extracted_tools:
            print("⚠️ No extracted tools found, falling back to direct search")
            search_results = self.firecrawl.search_companies(state.query, num_results=4)
            if search_results and search_results.web:
                tool_names = [
                    result.title for result in search_results.web if result.title
                ]
            else:
                tool_names = []
        else:
            tool_names = extracted_tools[:4]
        
        print(f"🔬 Researching specific tools: {', '.join(tool_names)}")

        companies = []

        for tool_name in tool_names:
            tool_search_results = self.firecrawl.search_companies(tool_name + " official site", num_results=1)

            if tool_search_results and tool_search_results.web:
                result = tool_search_results.web[0]
                url = result.url

                company = CompanyInfo(
                    name=tool_name,
                    # --- THIS IS THE FIX ---
                    # The search result object has a 'description' attribute, not 'markdown'.
                    description=result.description,
                    website=url,
                    tech_stack=[],
                    competitors=[]
                )

                scrapped = self.firecrawl.scrape_company_pages(url)
                if scrapped and scrapped.markdown:
                    content = scrapped.markdown
                    analysis = self._analyze_company_content(company.name, content)
                    
                    if analysis:
                        company.pricing_model = analysis.pricing_model
                        company.is_open_source = analysis.is_open_source
                        company.tech_stack = analysis.tech_stack 
                        # Only update the description if the analysis was successful
                        if analysis.description and "Failed" not in analysis.description:
                            company.description = analysis.description
                        company.api_available = analysis.api_available
                        company.language_support = analysis.language_support
                        company.integration_capabilities = analysis.integration_capabilities
                
                companies.append(company)
            
        return {"companies": companies}
    
    def _analyze_step(self, state: ResearchState) -> Dict[str, Any]:
        print("✨ Generating recommendations")

        company_data = ", ".join([
            company.json() for company in state.companies
        ])

        messages = [
            SystemMessage(content=self.prompts.RECOMMENDATIONS_SYSTEM),
            HumanMessage(content=self.prompts.recommendations_user(state.query, company_data))
        ]

        response = self.llm.invoke(messages)

        return {"analysis": response.content}
    

    def run(self, query: str) -> ResearchState:
        initial_state = ResearchState(query=query)
        final_state = self.workflow.invoke(initial_state)
        return ResearchState(**final_state)