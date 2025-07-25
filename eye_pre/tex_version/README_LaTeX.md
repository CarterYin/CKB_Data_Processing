# 疾病在种族群体中分布的综合分析报告 - LaTeX版本

## 文件说明

### 主要文件
- `final_bilingual_report.tex` - LaTeX源文件（中英双语）
- `final_bilingual_report.pdf` - 生成的PDF报告（156KB，11页）
- `compile_latex.sh` - 编译脚本

### 报告特色

#### 1. 专业排版设计
- **页面布局**：A4纸张，2.5cm边距，专业学术格式
- **字体配置**：
  - 中文：宋体（正文）+ 黑体（标题）
  - 英文：Times New Roman（正文）+ Arial（标题）
- **颜色方案**：
  - 标题蓝色（RGB: 0,82,155）
  - 章节蓝色（RGB: 0,102,204）
  - 子章节灰色（RGB: 102,102,102）

#### 2. 精美标题页
- 中英双语标题
- 研究基本信息表格
- 统计方法说明
- 自动日期生成

#### 3. 完整目录结构
- 自动生成目录
- 超链接导航
- 页码对应

#### 4. 专业表格设计
- 使用booktabs包的三线表
- 中英双语表头
- 自适应列宽
- 表格标题

#### 5. 高亮重要信息
- 彩色背景框突出关键发现
- 统计显著性结果高亮
- 重要提示框

#### 6. 页眉页脚
- 左页眉：中文标题
- 右页眉：英文标题
- 页脚：居中页码

## 编译方法

### 方法一：使用提供的脚本
```bash
chmod +x compile_latex.sh
./compile_latex.sh
```

### 方法二：手动编译
```bash
# 第一次编译
xelatex -interaction=nonstopmode final_bilingual_report.tex

# 第二次编译（生成目录）
xelatex -interaction=nonstopmode final_bilingual_report.tex

# 清理辅助文件
rm -f *.aux *.log *.toc *.out *.synctex.gz
```

## 系统要求

### LaTeX发行版
- **推荐**：TeX Live 2020或更新版本
- **替代**：MiKTeX（Windows）
- **必需引擎**：XeLaTeX（支持中文字体）

### 必需包
文档已包含所有必需的包声明：
- `xeCJK` - 中文支持
- `fontspec` - 字体管理
- `geometry` - 页面布局
- `booktabs` - 专业表格
- `xcolor` - 颜色支持
- `hyperref` - 超链接
- `fancyhdr` - 页眉页脚
- `titlesec` - 标题格式

### 字体要求
- **中文字体**：宋体（SimSun）、黑体（SimHei）
- **英文字体**：Times New Roman、Arial
- 注：macOS和Windows系统通常已预装这些字体

## 文档结构

### 1. 标题页
- 双语标题
- 研究信息表
- 方法说明

### 2. 目录页
- 自动生成
- 超链接导航

### 3. 正文章节
1. 执行摘要
2. 研究人群特征
3. 总体疾病患病率
4. 按种族群体分类的疾病患病率
5. 统计分析
6. 年龄调整分析
7. 疾病相关性和共病模式
8. 主成分分析
9. 临床意义和建议
10. 结论

### 4. 报告信息框
- 编制日期
- 样本信息
- 统计方法

## 自定义修改

### 修改颜色
在LaTeX文件开头的颜色定义部分：
```latex
\definecolor{titleblue}{RGB}{0,82,155}
\definecolor{sectionblue}{RGB}{0,102,204}
\definecolor{subsectiongray}{RGB}{102,102,102}
```

### 修改字体
```latex
\setCJKmainfont{SimSun}  % 中文正文字体
\setCJKsansfont{SimHei}  % 中文标题字体
\setmainfont{Times New Roman}  % 英文正文字体
\setsansfont{Arial}  % 英文标题字体
```

### 修改页面布局
```latex
\geometry{
    left=2.5cm,
    right=2.5cm,
    top=3cm,
    bottom=3cm,
    headheight=15pt
}
```

## 输出质量

- **页数**：11页
- **文件大小**：156KB
- **分辨率**：高质量PDF
- **字体**：矢量字体，可缩放
- **表格**：专业三线表格式
- **超链接**：支持目录导航

## 故障排除

### 编译错误
1. **字体未找到**：安装所需中英文字体
2. **包缺失**：更新LaTeX发行版
3. **编码问题**：确保使用UTF-8编码

### 常见警告
- 字体形状警告：正常，使用替代字体
- 行溢出警告：可忽略，不影响阅读
- 未使用包警告：可忽略

### 优化建议
- 使用SSD存储可加快编译速度
- 定期更新LaTeX发行版
- 使用现代LaTeX编辑器（如TeXworks、TeXstudio）

## 版本信息

- **创建日期**：2025年1月24日
- **LaTeX引擎**：XeLaTeX
- **文档类**：article
- **字体大小**：12pt
- **纸张大小**：A4

---

*此LaTeX文档提供了专业的学术报告排版，适合用于正式的研究报告、学术论文和会议文档。* 