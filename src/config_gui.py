#!/usr/bin/env python3
"""
邮件助手配置界面 - 为朋友准备的简易配置工具
"""

import os
import sys

# 设置环境变量抑制 Tk 弃用警告
os.environ['TK_SILENCE_DEPRECATION'] = '1'

import tkinter as tk
from tkinter import ttk, messagebox
import json


class ConfigGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("📧 邮件助手配置工具")
        self.root.geometry("500x450")
        
        # 设置窗口居中
        self.center_window()
        
        # 创建界面
        self.create_widgets()
        
        # 加载现有配置
        self.load_config()
    
    def center_window(self):
        """窗口居中显示"""
        self.root.update_idletasks()
        width = 500
        height = 450
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """创建界面元素"""
        # 标题
        title = ttk.Label(self.root, text="📧 邮件助手配置", 
                         font=('Helvetica', 16, 'bold'))
        title.pack(pady=20)
        
        # 说明文字
        desc = ttk.Label(self.root, 
                        text="请填写以下信息，这些信息将保存在本地",
                        wraplength=450)
        desc.pack(pady=5)
        
        # 创建输入框
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # QQ 邮箱
        ttk.Label(frame, text="QQ 邮箱：").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.qq_email = ttk.Entry(frame, width=35)
        self.qq_email.grid(row=0, column=1, pady=5, padx=5)
        self.qq_email.insert(0, "xxxx@qq.com")
        
        # QQ 授权码
        ttk.Label(frame, text="QQ 授权码：").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.qq_auth = ttk.Entry(frame, width=35, show="*")
        self.qq_auth.grid(row=1, column=1, pady=5, padx=5)
        
        # DeepSeek API Key
        ttk.Label(frame, text="DeepSeek Key：").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.deepseek_key = ttk.Entry(frame, width=35, show="*")
        self.deepseek_key.grid(row=2, column=1, pady=5, padx=5)
        
        # 帮助链接
        help_frame = ttk.Frame(self.root)
        help_frame.pack(pady=5)
        
        ttk.Label(help_frame, text="不知道如何获取？", foreground="blue", cursor="hand2").pack()
        
        # 提示文字
        tips = """
💡 提示：
• QQ 授权码：登录 QQ 邮箱 → 设置 → 账户 → 开启 IMAP/SMTP 服务
• DeepSeek Key：访问 platform.deepseek.com 注册获取（以 sk- 开头）
• 费用：DeepSeek API 很便宜，10-20 元够用很久
        """
        tip_label = ttk.Label(self.root, text=tips, wraplength=450, 
                             foreground="gray", justify=tk.LEFT)
        tip_label.pack(pady=10)
        
        # 按钮区域
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=15)
        
        ttk.Button(btn_frame, text="💾 保存配置", 
                  command=self.save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🧪 测试运行", 
                  command=self.test_run).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ 退出", 
                  command=self.root.quit).pack(side=tk.LEFT, padx=5)
    
    def load_config(self):
        """加载现有配置"""
        if os.path.exists("config.json"):
            try:
                with open("config.json", "r") as f:
                    config = json.load(f)
                self.qq_email.delete(0, tk.END)
                self.qq_email.insert(0, config.get("qq_email", ""))
                self.qq_auth.delete(0, tk.END)
                self.qq_auth.insert(0, config.get("qq_auth_code", ""))
                self.deepseek_key.delete(0, tk.END)
                self.deepseek_key.insert(0, config.get("deepseek_key", ""))
            except Exception as e:
                print(f"加载配置失败: {e}")
    
    def save_config(self):
        """保存配置"""
        qq = self.qq_email.get().strip()
        auth = self.qq_auth.get().strip()
        key = self.deepseek_key.get().strip()
        
        # 验证
        if not qq or not auth or not key:
            messagebox.showerror("错误", "请填写所有必填项！")
            return
        
        if "@" not in qq:
            messagebox.showerror("错误", "请输入有效的邮箱地址！")
            return
        
        if not key.startswith("sk-"):
            messagebox.showwarning("警告", "DeepSeek Key 应该以 sk- 开头，请确认是否正确")
        
        # 保存配置
        config = {
            "qq_email": qq,
            "qq_auth_code": auth,
            "deepseek_key": key,
            "imap_server": "imap.qq.com",
            "smtp_server": "smtp.qq.com"
        }
        
        try:
            with open("config.json", "w") as f:
                json.dump(config, f, indent=2)
            messagebox.showinfo("成功", "配置已保存！\n\n现在可以运行邮件助手了。")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")
    
    def test_run(self):
        """测试运行"""
        if not os.path.exists("config.json"):
            messagebox.showerror("错误", "请先保存配置！")
            return
        
        result = messagebox.askyesno("测试运行", 
            "这将运行邮件助手程序，检查是否能正常接收和发送邮件。\n\n确定继续吗？")
        if result:
            self.root.destroy()
            import subprocess
            subprocess.run(["python3", "final_email_assistant.py"])


def main():
    root = tk.Tk()
    
    # macOS 特定：确保窗口显示在最前面
    if sys.platform == 'darwin':
        root.lift()
        root.attributes('-topmost', True)
        root.after_idle(root.attributes, '-topmost', False)
        # 强制激活窗口
        root.focus_force()
    
    app = ConfigGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
