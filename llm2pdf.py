import os
import shutil
import asyncio
from typing import List
from langchain_community.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatAnthropic
from langchain_community.chat_models import ChatOpenAI
import traceback



OPENAI_API_KEY = ""

anthropic_api_key = ""
#统计token
import os
import asyncio
from typing import List
from langchain_community.llms import OpenAI


#claude-3-haiku-20240307 claude-3-opus-20240229 claude-3-sonnet-20240229
# Initialize the OpenAI API
#gpt-3.5-turbo-16k-0613 gpt-4-turbo-2024-04-09
# llm = ChatOpenAI(temperature=0,model='gpt-4-turbo-2024-04-09', openai_api_key=OPENAI_API_KEY, max_tokens=4000)



OPENAI_API_KEY = ""
anthropic_api_key = ""

llm = ChatAnthropic(temperature=0, model='claude-3-opus-20240229', anthropic_api_key=anthropic_api_key, max_tokens=4000)

latex_examples = r'''
原文: This is the first example sentence with \$E=mc^2\$ LaTeX code.
翻译: 这是第一个包含\$E=mc^2\$ LaTeX代码的示例句子。
原文: The second example is \$\int_0^1 x^2 dx = \frac{1}{3}\$ with more complex LaTeX.
翻译: 第二个示例是包含更复杂LaTeX代码\$\int_0^1 x^2 dx = \frac{1}{3}\$的句子。
原文: Here is the third example with \$\sum_{i=1}^n i = \frac{n(n+1)}{2}\$ LaTeX formula.
翻译: 这是第三个示例,其中包含LaTeX公式\$\sum_{i=1}^n i = \frac{n(n+1)}{2}\$。
原文: The fourth example demonstrates \$\lim_{x \to \infty} \frac{1}{x} = 0\$ with LaTeX limit.
翻译: 第四个示例展示了包含LaTeX极限\$\lim_{x \to \infty} \frac{1}{x} = 0\$的句子。
'''

classification_prompt = PromptTemplate(
    input_variables=["text", "latex_examples"],
    template=r'''
        你是一个翻译专家并且精通LaTex语法,
        请将以下LaTeX文档从英文翻译为中文,
        并保持相关的专业术语不需要翻译,直接给出翻译后的完整LaTeX文档内容,
        不需要任何额外的说明或确认以及不要"```latex"的包裹标签,
        如果文档中没有可翻译成中文的内容,请直接输出我给你的文档内容:
    ###我给你的内容开始###
    {text}
    ###我给你的内容结束###
        '''
)

async def translate_file(file_path: str) -> str:
    with open(file_path, 'r') as file:
        content = file.read()
        print(f'文件内容是:{content}')
    print(f'开始翻译...发送文档中...')
    translation_chain = LLMChain(llm=llm, prompt=classification_prompt)
    translated_content = await translation_chain.apredict(text=content, latex_examples=latex_examples)
    print(f'翻译好了:{translated_content[:50]}')

    if r'\documentclass' in translated_content:
        translated_content = translated_content.replace(r'\documentclass', r'\documentclass' + '\n' + r'\usepackage{ctex}')

    return translated_content

async def process_files(directory: str) -> List[str]:
    ctex_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ctex')
    if os.path.exists(ctex_dir):
        for filename in os.listdir(ctex_dir):
            shutil.copy(os.path.join(ctex_dir, filename), directory)

    tex_files = []
    main_tex_file = None
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".tex"):
                file_path = os.path.join(root, file)
                tex_files.append(file_path)

                with open(file_path, 'r') as f:
                    content = f.read()
                    if r'\begin{document}' in content:
                        main_tex_file = file

    print(f'读取目录...')
    translation_tasks = []
    for file_path in tex_files:
        translation_tasks.append(asyncio.create_task(translate_file(file_path)))

    translated_contents = await asyncio.gather(*translation_tasks)

    write_tasks = []
    for file_path, translated_content in zip(tex_files, translated_contents):
        write_tasks.append(asyncio.create_task(write_file(file_path, translated_content)))

    await asyncio.gather(*write_tasks)

    return main_tex_file

async def write_file(file_path: str, content: str):
    print(f'开始写入文件...')
    with open(file_path, 'w') as file:
        await asyncio.to_thread(file.write, content)

async def main(directory: str):
    try:
        main_tex_file = await process_files(directory)

        os.chdir(directory)
        print(f'开始执行命令...开始编译文件{main_tex_file}')

        outfile = directory.split("/")[-1]

        os.system(f"xelatex -output-directory=/Downloads -jobname=chinese_{outfile} {main_tex_file}")
        print(f'文件输出路径在{os.getcwd()}')
    except Exception as e:
        print(f"发生错误: {str(e)}")
        traceback.print_exc()

directory = "/Downloads/arXiv-2204.03089v1"

asyncio.run(main(directory))
