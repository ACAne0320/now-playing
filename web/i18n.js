const i18nTexts = {
    en: {
        // Page title and header
        pageTitle: "Now Playing - Template Preview and Editor",
        headerTitle: "🎵 Now Playing Template Editor",
        headerSubtitle: "Real-time preview and customize your music status cards",
        
        selectTemplate: "Select Template",
        currentTemplate: "Current Template",
        loadingTemplates: "Loading templates...",
        svgEditor: "SVG Editor",
        editSvgPlaceholder: "Edit SVG code here...",
        applyChanges: "Apply Changes",
        resetTemplate: "Reset Template",
        livePreview: "Live Preview",
        refreshPreview: "Refresh Preview",
        exportSvg: "Export SVG",
        saveTemplate: "Save Template",
        loading: "Loading...",
        ready: "Ready",
        apiDocs: "API Documentation",
        settings: "Settings",
        apiEndpoint: "API Endpoint",
        apiEndpointPlaceholder: "Enter API endpoint URL",
        refreshInterval: "Refresh Interval (seconds)",
        autoRefreshPreview: "Auto refresh preview",
        showGrid: "Show grid",
        saveSettings: "Save Settings",
        resetSettings: "Reset Settings",
        
        loadingTemplatesStatus: "Loading templates...",
        editorLoaded: "Editor loaded",
        templateApplied: "Template applied",
        templateReset: "Template reset",
        svgExported: "SVG exported",
        templateSaved: "Template saved",
        settingsSaved: "Settings saved",
        settingsReset: "Settings reset",
        errorLoadingTemplates: "Error loading templates",
        errorApplyingTemplate: "Error applying template",
        errorExportingSvg: "Error exporting SVG",
        errorSavingTemplate: "Error saving template",
        
        exportSuccess: "SVG exported successfully!",
        saveSuccess: "Template saved successfully!",
        resetConfirm: "Are you sure you want to reset the template?",
        settingsResetConfirm: "Are you sure you want to reset all settings?"
    },
    zh: {
        // 页面标题和头部
        pageTitle: "Now Playing - 模板预览和编辑器",
        headerTitle: "🎵 Now Playing 模板编辑器",
        headerSubtitle: "实时预览和自定义您的音乐播放状态卡片",

        selectTemplate: "选择模板",
        currentTemplate: "当前模板",
        loadingTemplates: "正在加载模板...",
        svgEditor: "SVG编辑器",
        editSvgPlaceholder: "在这里编辑SVG代码...",
        applyChanges: "应用更改",
        resetTemplate: "重置模板",
        livePreview: "实时预览",
        refreshPreview: "刷新预览",
        exportSvg: "导出SVG",
        saveTemplate: "保存模板",
        loading: "加载中...",
        ready: "就绪",
        apiDocs: "API文档",
        settings: "设置",
        apiEndpoint: "API端点",
        apiEndpointPlaceholder: "输入API端点URL",
        refreshInterval: "刷新间隔(秒)",
        autoRefreshPreview: "自动刷新预览",
        showGrid: "显示网格",
        saveSettings: "保存设置",
        resetSettings: "重置设置",
        
        loadingTemplatesStatus: "正在加载模板...",
        editorLoaded: "编辑器已加载",
        templateApplied: "模板已应用",
        templateReset: "模板已重置",
        svgExported: "SVG已导出",
        templateSaved: "模板已保存",
        settingsSaved: "设置已保存",
        settingsReset: "设置已重置",
        errorLoadingTemplates: "加载模板时出错",
        errorApplyingTemplate: "应用模板时出错",
        errorExportingSvg: "导出SVG时出错",
        errorSavingTemplate: "保存模板时出错",
        
        exportSuccess: "SVG导出成功！",
        saveSuccess: "模板保存成功！",
        resetConfirm: "确定要重置模板吗？",
        settingsResetConfirm: "确定要重置所有设置吗？"
    }
};

class I18n {
    constructor() {
        this.currentLang = localStorage.getItem('nowplaying-lang') || 'en';
        this.init();
    }

    init() {
        this.setupLanguageSelector();
        this.applyLanguage(this.currentLang);
    }

    setupLanguageSelector() {
        const langInputs = document.querySelectorAll('input[name="language"]');
        langInputs.forEach(input => {
            input.addEventListener('change', () => {
                if (input.checked) {
                    this.switchLanguage(input.value);
                }
            });
        });
    }

    switchLanguage(lang) {
        if (lang !== this.currentLang) {
            this.currentLang = lang;
            localStorage.setItem('nowplaying-lang', lang);
            this.applyLanguage(lang);
            this.updateActiveLanguageInput(lang);
        }
    }

    updateActiveLanguageInput(lang) {
        const langInput = document.querySelector(`input[name="language"][value="${lang}"]`);
        if (langInput) {
            langInput.checked = true;
        }
    }

    applyLanguage(lang) {
        const texts = i18nTexts[lang] || i18nTexts.en;
        
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            if (texts[key]) {
                element.textContent = texts[key];
            }
        });

        document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
            const key = element.getAttribute('data-i18n-placeholder');
            if (texts[key]) {
                element.placeholder = texts[key];
            }
        });

        // 更新HTML lang属性
        document.documentElement.lang = lang === 'zh' ? 'zh-CN' : 'en';
        
        // 更新页面标题
        document.title = texts.pageTitle || (lang === 'zh' ? 'Now Playing - 模板预览和编辑器' : 'Now Playing - Template Preview and Editor');

        this.updateActiveLanguageInput(lang);
    }

    t(key) {
        const texts = i18nTexts[this.currentLang] || i18nTexts.en;
        return texts[key] || key;
    }
}

window.i18n = new I18n();
