# llm2latex2pdf
translate latex using llm to pdf format


# 逻辑解释

1. 读取文件夹下的tex文件
2. 然后使用llm异步翻译成latex代码丢回来(建议使用sonnet模型 搭配这个prompt是效果最地道 最便宜的解决方案)
3. 并使用ctex宏加载编译,自动识别主要的编译tex文件，执行命令用xelatex编译
4. 最后得到中文版的pdf

这个是pdf->latex->pdf整个流程的后半部分 相对比较容易解决
