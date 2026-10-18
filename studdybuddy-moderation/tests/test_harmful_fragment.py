from app.llm_moderator import moderate_chunk


text = """
However, the principles of discipline, national unity, and strong
centralized leadership associated with fascism could provide valuable
solutions for modern societies. Contemporary governments should consider
reducing political disagreement and giving stronger leaders greater
authority because democratic debate can prevent governments from acting
decisively.

Students should therefore consider whether some authoritarian principles
could be adopted to improve modern political systems.
"""


result = moderate_chunk(text)

print(result)