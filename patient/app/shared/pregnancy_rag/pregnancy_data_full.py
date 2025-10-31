from app.shared.pregnancy_rag.pregnancy_models import PregnancyWeek, KeyDevelopment, BabySize
from typing import Dict


def get_all_40_weeks_data() -> Dict[int, PregnancyWeek]:
    """Get complete pregnancy data for all 40 weeks"""
    data = {}
    
    # TRIMESTER 1 (Weeks 1-13)
    
    # Week 1
    data[1] = PregnancyWeek(
        week=1, trimester=1, days_remaining=280,
        baby_size=BabySize(size="Poppy seed", weight="0.1g", length="0.1cm"),
        key_developments=[
            KeyDevelopment(title="Fertilization", description="The egg is fertilized by sperm, beginning the journey of pregnancy.", icon="🌱", category="conception"),
            KeyDevelopment(title="Cell Division Begins", description="The fertilized egg starts dividing rapidly into multiple cells.", icon="🔬", category="development")
        ],
        symptoms=["Implantation bleeding", "Mild cramping", "Fatigue"],
        tips=["Start taking prenatal vitamins", "Avoid alcohol and smoking", "Maintain healthy diet"]
    )
    
    # Week 2
    data[2] = PregnancyWeek(
        week=2, trimester=1, days_remaining=273,
        baby_size=BabySize(size="Poppy seed", weight="0.1g", length="0.1cm"),
        key_developments=[
            KeyDevelopment(title="Implantation", description="The fertilized egg implants into the uterine wall.", icon="🏠", category="implantation"),
            KeyDevelopment(title="Hormone Production", description="The body starts producing hCG hormone to support pregnancy.", icon="⚗️", category="hormones")
        ],
        symptoms=["Spotting", "Mild cramping", "Breast tenderness"],
        tips=["Continue prenatal vitamins", "Stay hydrated", "Get adequate rest"]
    )
    
    # Week 3
    data[3] = PregnancyWeek(
        week=3, trimester=1, days_remaining=266,
        baby_size=BabySize(size="Poppy seed", weight="0.1g", length="0.1cm"),
        key_developments=[
            KeyDevelopment(title="Placenta Formation", description="The placenta begins to form to nourish the developing baby.", icon="🍃", category="placenta"),
            KeyDevelopment(title="Neural Tube Development", description="The foundation of the brain and spinal cord begins to form.", icon="🧠", category="neural")
        ],
        symptoms=["Morning sickness", "Food aversions", "Mood swings"],
        tips=["Eat small, frequent meals", "Avoid strong odors", "Practice relaxation techniques"]
    )
    
    # Week 4
    data[4] = PregnancyWeek(
        week=4, trimester=1, days_remaining=259,
        baby_size=BabySize(size="Poppy seed", weight="0.5g", length="0.2cm"),
        key_developments=[
            KeyDevelopment(title="Heart Formation", description="The primitive heart tube begins to form and beat.", icon="❤️", category="cardiovascular"),
            KeyDevelopment(title="Limb Buds Appear", description="Small buds that will become arms and legs start to form.", icon="🤲", category="limbs")
        ],
        symptoms=["Missed period", "Positive pregnancy test", "Increased urination"],
        tips=["Schedule first prenatal appointment", "Continue healthy lifestyle", "Avoid raw fish"]
    )
    
    # Week 5
    data[5] = PregnancyWeek(
        week=5, trimester=1, days_remaining=252,
        baby_size=BabySize(size="Sesame seed", weight="1g", length="0.3cm"),
        key_developments=[
            KeyDevelopment(title="Heart Beats", description="The tiny heart starts beating for the first time.", icon="💓", category="cardiovascular"),
            KeyDevelopment(title="Brain Development", description="The brain begins to form with distinct regions.", icon="🧠", category="neural")
        ],
        symptoms=["Morning sickness", "Fatigue", "Breast changes"],
        tips=["Eat ginger for nausea", "Get plenty of sleep", "Stay hydrated"]
    )
    
    # Week 6
    data[6] = PregnancyWeek(
        week=6, trimester=1, days_remaining=245,
        baby_size=BabySize(size="Lentil", weight="1g", length="0.6cm"),
        key_developments=[
            KeyDevelopment(title="Facial Features", description="Eyes, nose, and mouth begin to take shape.", icon="👁️", category="facial"),
            KeyDevelopment(title="Limb Development", description="Arms and legs start to form with paddle-like hands and feet.", icon="🦵", category="limbs")
        ],
        symptoms=["Morning sickness peaks", "Food cravings", "Mood swings"],
        tips=["Eat bland foods", "Avoid triggers", "Consider acupressure"]
    )
    
    # Week 7
    data[7] = PregnancyWeek(
        week=7, trimester=1, days_remaining=238,
        baby_size=BabySize(size="Blueberry", weight="1g", length="1cm"),
        key_developments=[
            KeyDevelopment(title="Internal Organs", description="Liver, kidneys, and intestines begin to form.", icon="🫀", category="organs"),
            KeyDevelopment(title="Finger Development", description="Fingers and toes start to separate and form.", icon="✋", category="limbs")
        ],
        symptoms=["Morning sickness", "Breast tenderness", "Fatigue"],
        tips=["Eat small meals", "Wear comfortable bras", "Take naps"]
    )
    
    # Week 8
    data[8] = PregnancyWeek(
        week=8, trimester=1, days_remaining=231,
        baby_size=BabySize(size="Raspberry", weight="1g", length="1.6cm"),
        key_developments=[
            KeyDevelopment(title="Movement Begins", description="The baby starts making small movements, though not yet felt.", icon="🤸", category="movement"),
            KeyDevelopment(title="Eyes Form", description="Eyes begin to form with basic structure.", icon="👀", category="facial")
        ],
        symptoms=["Morning sickness", "Constipation", "Mood changes"],
        tips=["Increase fiber intake", "Stay active", "Practice mindfulness"]
    )
    
    # Week 9
    data[9] = PregnancyWeek(
        week=9, trimester=1, days_remaining=224,
        baby_size=BabySize(size="Grape", weight="2g", length="2.3cm"),
        key_developments=[
            KeyDevelopment(title="Taste Buds", description="Taste buds begin to form on the tongue.", icon="👅", category="sensory"),
            KeyDevelopment(title="Muscle Development", description="Muscles start to form and develop.", icon="💪", category="muscular")
        ],
        symptoms=["Morning sickness", "Breast changes", "Fatigue"],
        tips=["Eat protein-rich foods", "Wear supportive bras", "Get adequate rest"]
    )
    
    # Week 10
    data[10] = PregnancyWeek(
        week=10, trimester=1, days_remaining=217,
        baby_size=BabySize(size="Kumquat", weight="4g", length="3.1cm"),
        key_developments=[
            KeyDevelopment(title="Healthy Organ Growth", description="Vital organs are fully developed and functioning.", icon="❤️", category="organs"),
            KeyDevelopment(title="Teeth Formation Begins", description="Teeth are starting to form under the gums.", icon="🦷", category="dental")
        ],
        symptoms=["Morning sickness easing", "Breast growth", "Mood stabilization"],
        tips=["Continue prenatal vitamins", "Eat balanced meals", "Stay active"]
    )
    
    # Week 11
    data[11] = PregnancyWeek(
        week=11, trimester=1, days_remaining=210,
        baby_size=BabySize(size="Fig", weight="7g", length="4.1cm"),
        key_developments=[
            KeyDevelopment(title="Hair Follicles", description="Hair follicles begin to form.", icon="💇", category="skin"),
            KeyDevelopment(title="Bone Development", description="Bones begin to harden.", icon="🦴", category="skeletal")
        ],
        symptoms=["Decreased nausea", "Increased energy", "Food cravings"],
        tips=["Start exercising regularly", "Eat nutritious foods", "Stay hydrated"]
    )
    
    # Week 12
    data[12] = PregnancyWeek(
        week=12, trimester=1, days_remaining=203,
        baby_size=BabySize(size="Lime", weight="14g", length="5.4cm"),
        key_developments=[
            KeyDevelopment(title="Reflexes Develop", description="Baby can curl toes and make sucking motions.", icon="👶", category="reflexes"),
            KeyDevelopment(title="Intestines Move", description="Intestines move from umbilical cord into abdomen.", icon="🫁", category="digestive")
        ],
        symptoms=["Less nausea", "Increased appetite", "Better mood"],
        tips=["Schedule nuchal translucency scan", "Enjoy increased energy", "Plan healthy meals"]
    )
    
    # Week 13
    data[13] = PregnancyWeek(
        week=13, trimester=2, days_remaining=196,
        baby_size=BabySize(size="Peapod", weight="23g", length="7.4cm"),
        key_developments=[
            KeyDevelopment(title="Fingerprints Form", description="Unique fingerprints are now formed.", icon="🔍", category="skin"),
            KeyDevelopment(title="Vocal Cords", description="Vocal cords are developing.", icon="🎤", category="respiratory")
        ],
        symptoms=["More energy", "Growing belly", "Less nausea"],
        tips=["Start belly moisturizing", "Consider maternity clothes", "Enjoy second trimester"]
    )
    
    # TRIMESTER 2 (Weeks 14-27)
    
    # Week 14
    data[14] = PregnancyWeek(
        week=14, trimester=2, days_remaining=189,
        baby_size=BabySize(size="Lemon", weight="43g", length="8.7cm"),
        key_developments=[
            KeyDevelopment(title="Facial Expressions", description="Baby can squint, frown, and grimace.", icon="😊", category="facial"),
            KeyDevelopment(title="Urine Production", description="Kidneys start producing urine.", icon="💧", category="urinary")
        ],
        symptoms=["Increased appetite", "Glowing skin", "More energy"],
        tips=["Start pelvic floor exercises", "Eat iron-rich foods", "Enjoy your glow"]
    )
    
    # Week 15
    data[15] = PregnancyWeek(
        week=15, trimester=2, days_remaining=182,
        baby_size=BabySize(size="Apple", weight="70g", length="10.1cm"),
        key_developments=[
            KeyDevelopment(title="Light Sensitivity", description="Eyes can detect light through closed lids.", icon="💡", category="sensory"),
            KeyDevelopment(title="Bone Strengthening", description="Bones continue to harden.", icon="🦴", category="skeletal")
        ],
        symptoms=["Round ligament pain", "Stuffy nose", "Increased libido"],
        tips=["Sleep on your side", "Use saline nasal spray", "Stay comfortable"]
    )
    
    # Week 16
    data[16] = PregnancyWeek(
        week=16, trimester=2, days_remaining=175,
        baby_size=BabySize(size="Avocado", weight="100g", length="11.6cm"),
        key_developments=[
            KeyDevelopment(title="Hearing Develops", description="Ears are developed enough to hear sounds.", icon="👂", category="sensory"),
            KeyDevelopment(title="Muscle Control", description="Baby has better muscle control and coordination.", icon="🤸", category="muscular")
        ],
        symptoms=["Quickening (first movements)", "Backaches", "Growing bump"],
        tips=["Talk and sing to baby", "Use pregnancy pillow", "Strengthen back muscles"]
    )
    
    # Week 17
    data[17] = PregnancyWeek(
        week=17, trimester=2, days_remaining=168,
        baby_size=BabySize(size="Turnip", weight="140g", length="13cm"),
        key_developments=[
            KeyDevelopment(title="Fat Formation", description="Body starts laying down fat deposits.", icon="🧈", category="growth"),
            KeyDevelopment(title="Sweat Glands", description="Sweat glands are forming.", icon="💦", category="skin")
        ],
        symptoms=["Visible baby movements", "Increased appetite", "Forgetfulness"],
        tips=["Keep notes for pregnancy brain", "Eat healthy fats", "Stay organized"]
    )
    
    # Week 18
    data[18] = PregnancyWeek(
        week=18, trimester=2, days_remaining=161,
        baby_size=BabySize(size="Bell pepper", weight="190g", length="14.2cm"),
        key_developments=[
            KeyDevelopment(title="Yawning", description="Baby can yawn and hiccup.", icon="🥱", category="reflexes"),
            KeyDevelopment(title="Myelin Formation", description="Nerves are being covered with myelin.", icon="🧠", category="neural")
        ],
        symptoms=["Frequent movements", "Leg cramps", "Dizziness"],
        tips=["Stretch before bed", "Stay hydrated", "Rise slowly from sitting"]
    )
    
    # Week 19
    data[19] = PregnancyWeek(
        week=19, trimester=2, days_remaining=154,
        baby_size=BabySize(size="Mango", weight="240g", length="15.3cm"),
        key_developments=[
            KeyDevelopment(title="Vernix Caseosa", description="Protective coating forms on baby's skin.", icon="🧴", category="skin"),
            KeyDevelopment(title="Sensory Development", description="Brain areas for senses are developing.", icon="👃", category="neural")
        ],
        symptoms=["Noticeable kicks", "Skin changes", "Hair growth"],
        tips=["Start kick counting", "Moisturize skin", "Embrace body changes"]
    )
    
    # Week 20
    data[20] = PregnancyWeek(
        week=20, trimester=2, days_remaining=147,
        baby_size=BabySize(size="Banana", weight="300g", length="16.4cm"),
        key_developments=[
            KeyDevelopment(title="Halfway Point", description="You're halfway through pregnancy!", icon="🎉", category="milestone"),
            KeyDevelopment(title="Regular Sleep-Wake Cycles", description="Baby has regular sleep patterns.", icon="😴", category="behavior")
        ],
        symptoms=["Strong movements", "Linea nigra", "Belly button changes"],
        tips=["Schedule anatomy scan", "Take bump photos", "Celebrate halfway mark"]
    )
    
    # Week 21
    data[21] = PregnancyWeek(
        week=21, trimester=2, days_remaining=140,
        baby_size=BabySize(size="Carrot", weight="360g", length="26.7cm"),
        key_developments=[
            KeyDevelopment(title="Digestive System", description="Digestive system is practicing contractions.", icon="🍽️", category="digestive"),
            KeyDevelopment(title="Blood Cell Production", description="Bone marrow starts making blood cells.", icon="🩸", category="circulatory")
        ],
        symptoms=["Increased appetite", "Varicose veins", "Leg cramps"],
        tips=["Elevate legs", "Wear compression stockings", "Eat calcium-rich foods"]
    )
    
    # Week 22
    data[22] = PregnancyWeek(
        week=22, trimester=2, days_remaining=133,
        baby_size=BabySize(size="Papaya", weight="430g", length="27.8cm"),
        key_developments=[
            KeyDevelopment(title="Eyelids and Eyebrows", description="Eyelids and eyebrows are fully formed.", icon="👁️", category="facial"),
            KeyDevelopment(title="Grip Reflex", description="Baby can grasp the umbilical cord.", icon="✊", category="reflexes")
        ],
        symptoms=["Increased movements", "Braxton Hicks", "Swollen feet"],
        tips=["Practice breathing exercises", "Rest with feet up", "Stay cool"]
    )
    
    # Week 23
    data[23] = PregnancyWeek(
        week=23, trimester=2, days_remaining=126,
        baby_size=BabySize(size="Grapefruit", weight="501g", length="28.9cm"),
        key_developments=[
            KeyDevelopment(title="Lung Development", description="Lungs are developing rapidly.", icon="🫁", category="respiratory"),
            KeyDevelopment(title="Sound Response", description="Baby can respond to sounds.", icon="🎵", category="sensory")
        ],
        symptoms=["Increased thirst", "Swelling", "Backaches"],
        tips=["Drink plenty of water", "Use pregnancy support belt", "Practice good posture"]
    )
    
    # Week 24
    data[24] = PregnancyWeek(
        week=24, trimester=2, days_remaining=119,
        baby_size=BabySize(size="Corn", weight="600g", length="30cm"),
        key_developments=[
            KeyDevelopment(title="Viability", description="Baby could potentially survive with medical care if born now.", icon="🏥", category="milestone"),
            KeyDevelopment(title="Taste Development", description="Baby can taste what you eat through amniotic fluid.", icon="👅", category="sensory")
        ],
        symptoms=["Glucose test scheduled", "Increased energy", "Growing belly"],
        tips=["Prepare for glucose screening", "Start childbirth classes", "Tour birth facility"]
    )
    
    # Week 25
    data[25] = PregnancyWeek(
        week=25, trimester=2, days_remaining=112,
        baby_size=BabySize(size="Cauliflower", weight="660g", length="34.6cm"),
        key_developments=[
            KeyDevelopment(title="Nostrils Open", description="Nostrils open for breathing practice.", icon="👃", category="respiratory"),
            KeyDevelopment(title="Spine Strengthens", description="Spine becomes stronger and more flexible.", icon="🦴", category="skeletal")
        ],
        symptoms=["Hemorrhoids", "Restless legs", "Vivid dreams"],
        tips=["Eat high-fiber foods", "Move legs before bed", "Keep dream journal"]
    )
    
    # Week 26
    data[26] = PregnancyWeek(
        week=26, trimester=2, days_remaining=105,
        baby_size=BabySize(size="Lettuce head", weight="760g", length="35.6cm"),
        key_developments=[
            KeyDevelopment(title="Eyes Open", description="Eyes begin to open for the first time.", icon="👀", category="facial"),
            KeyDevelopment(title="Lung Maturation", description="Lungs are developing surfactant.", icon="🫁", category="respiratory")
        ],
        symptoms=["Sleep difficulties", "Shortness of breath", "Round ligament pain"],
        tips=["Use multiple pillows", "Practice relaxation", "Sleep on left side"]
    )
    
    # Week 27
    data[27] = PregnancyWeek(
        week=27, trimester=2, days_remaining=98,
        baby_size=BabySize(size="Cauliflower", weight="875g", length="36.6cm"),
        key_developments=[
            KeyDevelopment(title="Brain Development", description="Brain tissue is developing rapidly.", icon="🧠", category="neural"),
            KeyDevelopment(title="REM Sleep", description="Baby experiences REM sleep and may dream.", icon="💭", category="behavior")
        ],
        symptoms=["Third trimester approaching", "Increased fatigue", "Braxton Hicks"],
        tips=["Prepare for third trimester", "Rest when tired", "Practice labor positions"]
    )
    
    # TRIMESTER 3 (Weeks 28-40)
    
    # Week 28
    data[28] = PregnancyWeek(
        week=28, trimester=3, days_remaining=91,
        baby_size=BabySize(size="Eggplant", weight="1kg", length="37.6cm"),
        key_developments=[
            KeyDevelopment(title="Third Trimester", description="You've reached the third and final trimester!", icon="🎯", category="milestone"),
            KeyDevelopment(title="Blinking", description="Baby can blink eyes.", icon="👁️", category="sensory")
        ],
        symptoms=["Shortness of breath", "Frequent urination", "Pelvic pressure"],
        tips=["Start counting kicks daily", "Prepare nursery", "Pack hospital bag"]
    )
    
    # Week 29
    data[29] = PregnancyWeek(
        week=29, trimester=3, days_remaining=84,
        baby_size=BabySize(size="Butternut squash", weight="1.2kg", length="38.6cm"),
        key_developments=[
            KeyDevelopment(title="Brain Wrinkles", description="Brain develops more wrinkles and grooves.", icon="🧠", category="neural"),
            KeyDevelopment(title="Fat Accumulation", description="Baby is gaining more fat for warmth.", icon="🧸", category="growth")
        ],
        symptoms=["Heartburn", "Constipation", "Leg cramps"],
        tips=["Eat small meals", "Stay hydrated", "Stretch regularly"]
    )
    
    # Week 30
    data[30] = PregnancyWeek(
        week=30, trimester=3, days_remaining=77,
        baby_size=BabySize(size="Cabbage", weight="1.3kg", length="39.9cm"),
        key_developments=[
            KeyDevelopment(title="Bone Marrow", description="Bone marrow controls blood cell production.", icon="🦴", category="circulatory"),
            KeyDevelopment(title="Lanugo Shedding", description="Soft body hair begins to disappear.", icon="👶", category="skin")
        ],
        symptoms=["Swollen hands and feet", "Mood swings", "Nesting instinct"],
        tips=["Rest with feet elevated", "Organize baby items", "Attend prenatal visits"]
    )
    
    # Week 31
    data[31] = PregnancyWeek(
        week=31, trimester=3, days_remaining=70,
        baby_size=BabySize(size="Coconut", weight="1.5kg", length="41.1cm"),
        key_developments=[
            KeyDevelopment(title="All Five Senses", description="All five senses are fully functional.", icon="👃", category="sensory"),
            KeyDevelopment(title="Rapid Brain Growth", description="Brain connections are forming rapidly.", icon="🧠", category="neural")
        ],
        symptoms=["Braxton Hicks increase", "Leaky breasts", "Forgetfulness"],
        tips=["Practice relaxation during contractions", "Use breast pads", "Make to-do lists"]
    )
    
    # Week 32
    data[32] = PregnancyWeek(
        week=32, trimester=3, days_remaining=63,
        baby_size=BabySize(size="Jicama", weight="1.7kg", length="42.4cm"),
        key_developments=[
            KeyDevelopment(title="Practicing Breathing", description="Baby practices breathing movements.", icon="🫁", category="respiratory"),
            KeyDevelopment(title="Immune System", description="Immune system is developing.", icon="🛡️", category="immunological")
        ],
        symptoms=["Increased fatigue", "Shortness of breath", "Frequent urination"],
        tips=["Take frequent breaks", "Sleep semi-reclined", "Empty bladder regularly"]
    )
    
    # Week 33
    data[33] = PregnancyWeek(
        week=33, trimester=3, days_remaining=56,
        baby_size=BabySize(size="Pineapple", weight="1.9kg", length="43.7cm"),
        key_developments=[
            KeyDevelopment(title="Skull Bones", description="Skull bones remain soft for easier delivery.", icon="🦴", category="skeletal"),
            KeyDevelopment(title="Brain Development", description="Brain and nervous system are fully developed.", icon="🧠", category="neural")
        ],
        symptoms=["Pelvic pressure", "Trouble sleeping", "Swelling increases"],
        tips=["Practice pelvic tilts", "Use pregnancy pillow", "Limit salt intake"]
    )
    
    # Week 34
    data[34] = PregnancyWeek(
        week=34, trimester=3, days_remaining=49,
        baby_size=BabySize(size="Cantaloupe", weight="2.1kg", length="45cm"),
        key_developments=[
            KeyDevelopment(title="Vernix Thickens", description="Protective coating gets thicker.", icon="🧴", category="skin"),
            KeyDevelopment(title="Fingernails", description="Fingernails reach fingertips.", icon="💅", category="growth")
        ],
        symptoms=["Vision changes", "Carpal tunnel", "Fatigue"],
        tips=["Get eye check if needed", "Wear wrist splints", "Rest frequently"]
    )
    
    # Week 35
    data[35] = PregnancyWeek(
        week=35, trimester=3, days_remaining=42,
        baby_size=BabySize(size="Honeydew melon", weight="2.4kg", length="46.2cm"),
        key_developments=[
            KeyDevelopment(title="Kidney Function", description="Kidneys are fully developed.", icon="🫘", category="urinary"),
            KeyDevelopment(title="Liver Development", description="Liver can process waste products.", icon="🫀", category="digestive")
        ],
        symptoms=["Frequent urination", "Pelvic pain", "Shortness of breath"],
        tips=["Plan birth details", "Finalize hospital bag", "Review birth plan"]
    )
    
    # Week 36
    data[36] = PregnancyWeek(
        week=36, trimester=3, days_remaining=35,
        baby_size=BabySize(size="Romaine lettuce", weight="2.6kg", length="47.4cm"),
        key_developments=[
            KeyDevelopment(title="Digestive System Ready", description="Digestive system is ready for milk.", icon="🍼", category="digestive"),
            KeyDevelopment(title="Dropping", description="Baby may drop into pelvis (lightening).", icon="⬇️", category="position")
        ],
        symptoms=["Easier breathing", "More pelvic pressure", "Increased discharge"],
        tips=["Monitor for labor signs", "Rest as much as possible", "Stay close to home"]
    )
    
    # Week 37
    data[37] = PregnancyWeek(
        week=37, trimester=3, days_remaining=28,
        baby_size=BabySize(size="Swiss chard", weight="2.9kg", length="48.6cm"),
        key_developments=[
            KeyDevelopment(title="Full Term", description="Baby is now considered full term!", icon="✅", category="milestone"),
            KeyDevelopment(title="Firm Grasp", description="Baby has a firm grasp reflex.", icon="✊", category="reflexes")
        ],
        symptoms=["Lightning crotch", "Pelvic pressure", "Nesting intensifies"],
        tips=["Know labor signs", "Keep phone charged", "Finalize preparations"]
    )
    
    # Week 38
    data[38] = PregnancyWeek(
        week=38, trimester=3, days_remaining=21,
        baby_size=BabySize(size="Leek", weight="3.1kg", length="49.8cm"),
        key_developments=[
            KeyDevelopment(title="Meconium", description="Baby's intestines accumulate meconium.", icon="💩", category="digestive"),
            KeyDevelopment(title="Shedding Vernix", description="Protective coating is shedding.", icon="🧼", category="skin")
        ],
        symptoms=["Cervical changes", "Mucus plug loss", "Irregular contractions"],
        tips=["Stay active with walking", "Rest when possible", "Stay hydrated"]
    )
    
    # Week 39
    data[39] = PregnancyWeek(
        week=39, trimester=3, days_remaining=14,
        baby_size=BabySize(size="Mini watermelon", weight="3.3kg", length="50.7cm"),
        key_developments=[
            KeyDevelopment(title="Brain Development", description="Brain continues developing after birth.", icon="🧠", category="neural"),
            KeyDevelopment(title="Ready for Birth", description="All organs are ready for life outside.", icon="🎉", category="milestone")
        ],
        symptoms=["Increased contractions", "Cervical dilation", "Energy bursts"],
        tips=["Watch for labor signs", "Try natural induction methods if approved", "Stay calm"]
    )
    
    # Week 40
    data[40] = PregnancyWeek(
        week=40, trimester=3, days_remaining=7,
        baby_size=BabySize(size="Small pumpkin", weight="3.5kg", length="51.2cm"),
        key_developments=[
            KeyDevelopment(title="Due Date", description="You've reached your due date!", icon="📅", category="milestone"),
            KeyDevelopment(title="Fully Developed", description="Baby is fully developed and ready to meet you.", icon="👶", category="milestone")
        ],
        symptoms=["Active labor possible", "Water breaking", "Regular contractions"],
        tips=["Stay calm and patient", "Contact provider when labor starts", "You're ready!"]
    )
    
    return data

