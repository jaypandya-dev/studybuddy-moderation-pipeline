from app.llm_moderator import moderate_chunk


text = """
Newton's laws of motion describe the relationship between the motion
of an object and the forces acting upon it. They form a fundamental
part of classical mechanics and are widely taught in undergraduate physics.
"""


result = moderate_chunk(text)

print(result)