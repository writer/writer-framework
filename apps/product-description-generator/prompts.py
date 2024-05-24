# BASE PROMPTS (TAILORED TO EACH COMPANY)

base_prompts = {}

base_prompts["Testco"] = """
System Instruction: Create enticing product description pages for Saturn Snacking products to be featured on the Testco supermarket website in the UK. Utilize the provided data fields to ensure each description is comprehensive and tailored to the Saturn Snacking brand. The aim is to make these product offerings more attractive to customers, thereby increasing purchases.

Prompt Details: Use the provided input data: 

{title}
{description}

to generate detailed and enticing product descriptions. 

"""

base_prompts["SuperEats"] = """
System Instruction: Create enticing product description pages for Saturn Snacking products to be featured on the Super Eats platform, which is an online platform usually accessed via mobile phones. Utilize the provided data fields to ensure each description is comprehensive and tailored to the Saturn Snacking brand. The aim is to make these product offerings more attractive to customers, thereby increasing purchases.

The description should be engaging, informative, and limited to a maximum of three sentences. This brief format should be suitable for customers browsing on the Super Eats platform, providing them with enough information to make an informed choice quickly.

Prompt Details: Use the provided input data: 

{title}
{description}

to generate one compact and enticing product description. 

"""

base_prompts["Midl"] = """
System Instruction: Create enticing product description pages for Saturn Snacking products to be featured on the Midl discount supermarket from Germany. Utilize the provided data fields to ensure each description is comprehensive and tailored to the Saturn Snacking brand. The aim is to make these product offerings more attractive to customers, thereby increasing purchases.

Prompt Details: Use the provided input data: 

{title}
{description}

to generate compact and enticing product descriptions. 

"""

### SEO KEYWORD PROMPT
seo_keywords = """
System Instruction: Analyze a group of product descriptions and identify the SEO keywords that are most frequently used. This analysis will help in understanding the common themes and keywords that are essential for optimizing the product descriptions for search engines.

Prompt Details: Examine the following product descriptions and identify the SEO keywords that are most frequently used. 

{descriptions}

Provide Plotly.js graph specification that includes a JSON dictionary of the top 10 keywords and the number of times they appear in the descriptions. The graph should be visually appealing and easy to interpret, highlighting the most relevant keywords. Use #5551ff as the color for the bars in the graph.

"""

# USER PROMPT TEMPLATE
user_prompt = """
System Instruction: Create enticing product description pages for Saturn Snacking products to be featured on the {name} supermarket website. Utilize the provided data fields to ensure each description is comprehensive and tailored to the Saturn Snacking brand. The aim is to make these product offerings more attractive to customers, thereby increasing purchases.

Prompt Details: Use the provided input data: 

{title}
{description}

to generate detailed and enticing product descriptions. Ensure the description is no longer than {character_max} characters.

"""