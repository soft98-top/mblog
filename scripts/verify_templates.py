#!/usr/bin/env python3
"""
验证模板文件的完整性和正确性
"""
from pathlib import Path
import sys

def verify_templates():
    """验证所有模板文件"""
    templates_dir = Path(__file__).parent.parent / "mblog" / "templates" / "project"
    
    # 必需的模板文件
    required_templates = [
        "config.json.template",
        "gen.py.template",
        "requirements.txt.template",
        "welcome.md.template",
        "deploy.yml.template",
        "deploy-dual-repo.yml.template",
        "gitmodules.template",
        "SETUP_GUIDE.md.template",
    ]
    
    print("🔍 验证模板文件...")
    print(f"模板目录: {templates_dir}")
    print()
    
    missing = []
    for template in required_templates:
        template_path = templates_dir / template
        if template_path.exists():
            size = template_path.stat().st_size
            print(f"✅ {template} ({size} bytes)")
        else:
            print(f"❌ {template} - 文件不存在")
            missing.append(template)
    
    print()
    
    if missing:
        print(f"❌ 缺少 {len(missing)} 个模板文件:")
        for template in missing:
            print(f"   - {template}")
        return False
    
    # 验证变量使用
    print("🔍 验证模板变量...")
    
    variables = {
        "gitmodules.template": ["{{CONTENT_REPO_URL}}"],
        "SETUP_GUIDE.md.template": ["{{CONTENT_REPO_URL}}", "{{PROJECT_NAME}}"],
    }
    
    for template, expected_vars in variables.items():
        template_path = templates_dir / template
        content = template_path.read_text(encoding='utf-8')
        
        for var in expected_vars:
            if var in content:
                print(f"✅ {template} 包含变量 {var}")
            else:
                print(f"❌ {template} 缺少变量 {var}")
                return False
    
    print()
    print("✅ 所有模板文件验证通过！")
    return True

if __name__ == "__main__":
    success = verify_templates()
    sys.exit(0 if success else 1)
