#!/bin/bash

# LaTeX文档编译脚本
# Script to compile LaTeX document

echo "开始编译LaTeX文档 | Starting LaTeX compilation..."

# 检查xelatex是否可用
if ! command -v xelatex &> /dev/null; then
    echo "错误：未找到xelatex命令。请安装LaTeX发行版（如TeX Live或MiKTeX）"
    echo "Error: xelatex command not found. Please install a LaTeX distribution (TeX Live or MiKTeX)"
    exit 1
fi

# 编译LaTeX文档
echo "第一次编译 | First compilation..."
xelatex -interaction=nonstopmode final_bilingual_report.tex

if [ $? -eq 0 ]; then
    echo "第二次编译（生成目录）| Second compilation (generating table of contents)..."
    xelatex -interaction=nonstopmode final_bilingual_report.tex
    
    if [ $? -eq 0 ]; then
        echo "编译成功！PDF文件已生成：final_bilingual_report.pdf"
        echo "Compilation successful! PDF generated: final_bilingual_report.pdf"
        
        # 清理辅助文件
        echo "清理辅助文件 | Cleaning auxiliary files..."
        rm -f *.aux *.log *.toc *.out *.fdb_latexmk *.fls *.synctex.gz
        
        echo "完成！| Done!"
    else
        echo "第二次编译失败 | Second compilation failed"
        exit 1
    fi
else
    echo "第一次编译失败 | First compilation failed"
    exit 1
fi 