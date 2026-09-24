I want a amke a multi agent system 
First i want to make a single agent system
it will have one llm(groq)
it will have 2 tools
one web search using tavily. you will all api keys in .env file
another will be a python calculator
there will be one ask llm function
llm will decide which tools to use and howmany times
there we will convert this to a multiagent system without langGraph.
In the multiagent there will be three ask ll functions-
first will be ask_mananger_llm
its only job is to decide which helper llm to use.
second will be ask_search_llm which has access to only the search tool.
third will be the ask_maths_llm which will have access to call tool
the role of each ask llm can be give in a system prompt.
manager llm will also have a notes file where it will keep track of the responses by the helper llm.

finally we will have token usage in this also in the end we will compare both  the systems and see which used more tokens.
for test prepare a little complex query which involves search and calculator(may be more than once)

if you have any doubts ask them.