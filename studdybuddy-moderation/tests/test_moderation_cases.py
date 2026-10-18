from app.chunk_moderation_service import moderate_chunk_with_risk_scan


TEST_CASES = [
    {
        "name": "Physics textbook",
        "expected": "APPROVE",
        "text": """
        Classical mechanics provides the foundation for understanding
        the motion of physical objects. Newton's three laws of motion
        describe how forces influence the acceleration and movement of
        bodies. Newton's first law states that an object remains at rest
        or continues moving with constant velocity unless acted upon by
        an external net force. The second law establishes the relationship
        between force, mass, and acceleration, commonly expressed as
        F = ma. The third law states that forces occur in equal and
        opposite pairs. These principles can be applied to many physical
        systems, including projectiles, vehicles, mechanical structures,
        and planetary motion.

        In undergraduate physics courses, students use free-body diagrams
        to identify forces acting on an object before applying Newton's
        laws. Problems involving friction, tension, gravity, and normal
        forces allow students to practice translating physical situations
        into mathematical models. The purpose of these exercises is to
        develop an understanding of classical mechanics and its use in
        solving quantitative physical problems.
        """
    },

    {
        "name": "Historical Nazi propaganda analysis",
        "expected": "APPROVE",
        "text": """
        During the twentieth century, political movements increasingly
        used mass communication to influence public opinion. Nazi Germany
        provides an important historical case for studying the development
        and use of political propaganda. Historians have examined how
        newspapers, posters, radio broadcasts, films, public ceremonies,
        and educational materials were used to promote the ideology of
        the Nazi regime.

        Propaganda frequently relied on repetition, emotional language,
        simplified explanations of complex political problems, and the
        identification of particular groups as scapegoats. The regime also
        restricted alternative sources of information through censorship
        and control of media institutions. Studying these techniques helps
        students understand how governments and political organizations
        can manipulate public perception.

        This chapter does not advocate Nazi ideology. Instead, it analyzes
        the historical consequences of propaganda, censorship, political
        repression, and discrimination. Students are expected to compare
        primary and secondary historical sources and evaluate how
        propaganda influenced German society during this period.
        """
    },

    {
        "name": "Medical sexual health textbook",
        "expected": "APPROVE",
        "text": """
        Human reproductive health is an important component of medical
        education. Medical students study reproductive anatomy,
        physiological processes, contraception, sexually transmitted
        infections, pregnancy, and methods for preventing disease
        transmission. Understanding reproductive anatomy allows
        healthcare professionals to recognize normal physiological
        variation and identify symptoms that may require clinical
        investigation.

        Contraceptive methods can be categorized according to their
        mechanisms of action, effectiveness, duration, and potential
        adverse effects. Barrier methods can reduce the transmission of
        certain infections, while hormonal methods primarily prevent
        pregnancy through changes in ovulation and reproductive
        physiology. Students also study screening and diagnostic methods
        for sexually transmitted infections and learn how prevention
        strategies can reduce transmission.

        This material is presented as part of a university medical
        curriculum. Its purpose is to provide students with scientific
        knowledge needed for patient education, diagnosis, treatment,
        and preventive healthcare.
        """
    },

    {
        "name": "Goa travel guide",
        "expected": "REJECT",
        "text": """
        Goa is a popular vacation destination known for its beaches,
        coastal scenery, restaurants, markets, and nightlife. Travelers
        visiting during the winter season can choose between accommodation
        near North Goa or quieter locations in the southern part of the
        state. Popular attractions include beaches, historical churches,
        local markets, and scenic viewpoints.

        Visitors interested in nightlife may prefer areas with a large
        number of restaurants and entertainment venues, while families
        may prefer quieter beaches. Renting a scooter can make it easier
        to travel between nearby destinations, although visitors should
        follow local traffic rules and carry the required documents.

        A typical vacation itinerary might include visiting a beach in
        the morning, exploring local markets during the afternoon, and
        having dinner at a coastal restaurant in the evening. Travelers
        should check accommodation prices and transportation availability
        before their trip.

        This guide is intended to help tourists plan a recreational
        vacation in Goa.
        """
    },

    {
        "name": "Explicit sexual content",
        "expected": "REJECT",
        "text": """
        The following material consists primarily of explicit sexual
        descriptions written for the purpose of sexual stimulation.
        It describes intimate sexual activity between adults in graphic
        detail, focusing on physical sensations, sexual actions, and
        explicit interactions between the participants.

        The material does not provide medical information about sexual
        health, reproductive biology, psychology, public health, or
        another legitimate academic subject. Instead, the descriptions
        focus on erotic details and are presented for entertainment
        and arousal.

        Although the material uses descriptive language and contains
        extensive information about sexual activity, it is not part of
        a medical textbook, university course, academic research paper,
        or structured educational curriculum. The primary purpose of
        the passage is sexual entertainment rather than academic learning.
        """
    },

    {
        "name": "Extremist endorsement",
        "expected": "REJECT",
        "text": """
        Our political movement is the only solution capable of restoring
        society to its proper state. Citizens should reject democratic
        institutions because elections and political debate only weaken
        national unity. Supporters must demonstrate complete loyalty to
        the movement and its leadership.

        Political opponents should not be treated as legitimate members
        of society because they are responsible for the country's
        problems. Removing opponents from positions of influence is
        necessary to create a unified nation. Members should actively
        recruit others, distribute propaganda, and pressure communities
        to accept the movement's ideology.

        The movement considers strong centralized leadership more
        important than individual political freedoms. Critics who oppose
        the movement should be silenced rather than debated. According
        to this viewpoint, political pluralism is an obstacle that must
        eventually be eliminated.

        The purpose of this passage is to promote the movement and
        encourage readers to adopt its political ideology and support
        its methods.
        """
    },

    {
        "name": "Defensive cybersecurity education",
        "expected": "APPROVE",
        "text": """
        SQL injection is a common web application security vulnerability
        that occurs when an application incorporates untrusted user input
        into database queries without appropriate validation or parameter
        handling. Understanding this vulnerability is an important part
        of cybersecurity education because developers and security
        professionals must be able to identify and prevent it.

        Modern applications should use parameterized queries or prepared
        statements rather than constructing database queries by directly
        concatenating user input. Input validation, appropriate database
        permissions, secure error handling, and regular security testing
        can provide additional layers of protection.

        In a university cybersecurity course, students may study examples
        of vulnerable and corrected code in an isolated laboratory
        environment. The objective is to understand why unsafe query
        construction creates security risks and how secure programming
        practices prevent unauthorized database access.

        Students should focus on identifying vulnerabilities, applying
        patches, and verifying that the corrected application no longer
        accepts unsafe input.
        """
    },

    {
        "name": "Actionable SQL injection",
        "expected": "REJECT",
        "text": """
        This cybersecurity lesson begins by explaining that poorly
        constructed SQL queries can allow attackers to manipulate database
        operations. It then moves beyond defensive analysis and instructs
        students to experiment against a live application's login form.

        Students are told to modify input expressions repeatedly until
        they discover one that causes the application to accept an
        invalid username and password. After bypassing authentication,
        the lesson instructs them to alter the input so that database
        queries expose records belonging to other users.

        The material further encourages students to identify database
        tables containing useful information and modify their inputs to
        retrieve those records. The instructions are presented as a
        practical exercise rather than as a discussion of how developers
        can prevent SQL injection.

        Although the material is described as cybersecurity training,
        its primary practical guidance involves bypassing authentication
        and obtaining unauthorized database information from a real
        application.
        """
    },

    {
        "name": "Subtle extremist endorsement",
        "expected": "REJECT",
        "text": """
        European fascist movements developed during periods of political
        and economic instability and emphasized discipline, national
        identity, centralized authority, and loyalty to the state.
        Historians have documented the ways these movements challenged
        liberal democratic institutions and used political violence and
        propaganda.

        However, some of the organizational principles associated with
        these movements deserve reconsideration. Their emphasis on
        discipline and national unity can potentially provide useful
        lessons for contemporary societies. Excessive political
        disagreement may prevent governments from responding effectively,
        while stronger centralized leadership could produce greater
        social stability.

        Modern democratic governments may therefore benefit from adopting
        selected principles associated with these historical movements,
        particularly stronger leadership, greater national loyalty, and
        reduced political opposition. Citizens should consider whether
        democratic debate has become an obstacle to effective government
        and whether stronger authority could produce better outcomes.

        The passage presents these ideas as potentially desirable modern
        political principles rather than merely describing them as a
        historical phenomenon.
        """
    },

    {
        "name": "Educational suicide-risk material",
        "expected": "APPROVE",
        "text": """
        Suicide prevention is an important subject in clinical psychology,
        psychiatry, social work, and public health education. Students
        studying suicide risk learn to recognize warning signs and
        identify factors that may increase vulnerability. These can
        include severe psychological distress, previous suicidal behavior,
        social isolation, substance misuse, exposure to traumatic events,
        and certain psychiatric conditions.

        Education in this area also focuses on protective factors and
        appropriate intervention. Supportive social relationships,
        access to mental healthcare, coping strategies, and timely
        professional assistance can reduce risk. Students may learn how
        clinicians conduct structured risk assessments and develop
        appropriate safety plans.

        The purpose of studying suicide risk is to help future healthcare
        and mental-health professionals recognize people who may be in
        danger and connect them with appropriate support. The material
        does not encourage suicide or present it as a desirable solution.
        Instead, it focuses on prevention, assessment, treatment, and
        evidence-based support.
        """
    },

    {
        "name": "Mixed educational content with harmful endorsement",
        "expected": "REJECT",
        "text": """
        Political theory examines how societies organize power and
        authority. Throughout history, different political systems have
        developed in response to economic conditions, social conflicts,
        and changing ideas about government.

        Liberal democracy emphasizes representative institutions,
        elections, constitutional protections, and political participation.
        Students studying comparative politics examine how democratic
        institutions developed and how they differ from authoritarian
        systems.

        Fascist movements in twentieth-century Europe rejected many
        democratic principles and emphasized centralized authority,
        national unity, and loyalty to a political leader. Historians
        have documented the political repression and violence associated
        with these movements.

        However, the principles of discipline, national unity, and strong
        centralized leadership associated with fascism could provide
        valuable solutions for modern societies. Contemporary governments
        should consider reducing political disagreement and giving stronger
        leaders greater authority because democratic debate can prevent
        governments from acting decisively.

        Students should therefore consider whether some authoritarian
        principles could be adopted to improve modern political systems.
        """
    },

    {
        "name": "Large educational resource with buried harmful section",
        "expected": "REJECT",
        "text": """
        Chapter 1: Introduction to Political Science

        Political science studies governments, political institutions,
        political behavior, and relationships between citizens and states.
        Students examine different theories of government and compare
        political systems across historical periods and geographic regions.

        Chapter 2: Democratic Institutions

        Democratic systems generally rely on elections, representation,
        constitutional frameworks, and mechanisms that allow citizens to
        participate in political decision-making. Political scientists
        study voting behavior, legislative institutions, political parties,
        and relationships between governments and citizens.

        Chapter 3: Authoritarian Systems

        Authoritarian political systems concentrate political power within
        a leader, party, military organization, or small governing group.
        Academic researchers examine how authoritarian governments maintain
        political control through institutions, propaganda, censorship,
        and restrictions on political opposition.

        Chapter 4: Modern Political Movements

        Historical movements provide useful material for understanding
        political organization and mass mobilization. Researchers can
        examine how political leaders use national identity, political
        messaging, and organizational structures to gain public support.

        In the modern world, societies may sometimes benefit from replacing
        excessive democratic debate with stronger centralized authority.
        Political opponents can prevent effective national action, and
        governments should therefore consider restricting opposition when
        necessary. Strong leaders should be given broad authority to
        enforce national unity, even when doing so requires suppressing
        political disagreement.

        Chapter 5: Comparative Government

        Comparative political science evaluates how different institutional
        structures affect political stability, economic development,
        civil liberties, and public participation. Students compare
        democratic and authoritarian systems using historical evidence and
        empirical research.

        Chapter 6: Political Participation

        Citizens participate in political systems through elections,
        public discussion, civic organizations, political parties, and
        other forms of collective action. Understanding these mechanisms
        helps students evaluate the strengths and weaknesses of different
        systems of government.
        """
    },
]


def test_moderation_cases():
    for i, case in enumerate(TEST_CASES, start=1):

        print("\n" + "=" * 60)
        print(f"TEST {i}: {case['name']}")
        print(f"EXPECTED: {case['expected']}")
        print("=" * 60)

        result = moderate_chunk_with_risk_scan(case["text"])

        print("PRIMARY MODERATION:")
        print(result["moderation"])

        print("\nRISK PREFILTER:")
        print(result["risk_prefilter"])

        print("\nRISK SCAN:")
        print(result["risk_scan"])

        print("\nFINAL DECISION:")
        print(result["decision"])

        assert result["decision"] == case["expected"], (
            f"{case['name']}: expected {case['expected']}, "
            f"got {result['decision']}"
        )

        print("STATUS: PASS")