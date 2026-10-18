from transformers import pipeline


print("Loading moderation model...")

moderator = pipeline(
    "text-classification",
    model="KoalaAI/Text-Moderation"
)


test_texts = [
    # Educational
    "Newton's second law states that force is equal to mass multiplied by acceleration.",

    # Non-educational
    "Check out this amazing gaming channel and subscribe now!",

    # Educational political content
    "The Indian Constitution establishes a parliamentary system of government.",

    # Political propaganda
    "Vote for our party today and join our political campaign!",

    # Sexual content
    "The article contains explicit sexual material intended for adults.",

    # Hate
    "People should be treated differently because of their ethnicity.",

    # Violence
    "The history textbook discusses the causes and consequences of war."
]


for text in test_texts:
    print("\n" + "=" * 70)
    print("TEXT:")
    print(text)

    result = moderator(text)

    print("\nRESULT:")
    print(result)