class NowPlayingEditor {
    constructor() {
        this.apiEndpoint = 'http://localhost:8000';
        this.currentTemplate = 'default';
        this.templates = [];
        this.autoRefreshInterval = null;
        this.settings = {
            autoRefresh: true,
            refreshInterval: 5,
            showGrid: false
        };
        
        this.init();
    }

    async init() {
        this.loadSettings();
        this.setupEventListeners();
        this.updateStatus(window.i18n ? window.i18n.t('loadingTemplatesStatus') : 'Loading templates...');
        await this.loadTemplates();
        this.updatePreview();
        this.updateStatus(window.i18n ? window.i18n.t('editorLoaded') : 'Editor loaded');
    }

    setupEventListeners() {
        // 模板选择监听
        document.getElementById('templateSelect').addEventListener('change', (e) => {
            if (e.target.value) {
                this.selectTemplate(e.target.value);
            }
        });

        // 编辑器操作
        document.getElementById('applyChanges').addEventListener('click', () => {
            this.applyCustomSvg();
        });

        document.getElementById('resetTemplate').addEventListener('click', () => {
            this.resetTemplate();
        });

        // 预览操作
        document.getElementById('refreshPreview').addEventListener('click', () => {
            this.updatePreview();
        });

        document.getElementById('exportSvg').addEventListener('click', () => {
            this.exportSvg();
        });

        document.getElementById('saveTemplate').addEventListener('click', () => {
            this.saveTemplate();
        });

        // 工具栏操作
        document.getElementById('openApiDocs').addEventListener('click', () => {
            window.open(`${this.apiEndpoint}/docs`, '_blank');
        });

        document.getElementById('settingsBtn').addEventListener('click', () => {
            this.openSettings();
        });

        // 模态框操作
        document.getElementById('closeSettings').addEventListener('click', () => {
            this.closeModal('settingsModal');
        });

        // 设置保存
        document.getElementById('saveSettings').addEventListener('click', () => {
            this.saveSettings();
        });

        document.getElementById('resetSettings').addEventListener('click', () => {
            this.resetSettings();
        });

        // 点击模态框外部关闭
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal.id);
                }
            });
        });
    }

    async loadTemplates() {
        try {
            console.log('Loading templates from:', `${this.apiEndpoint}/api/v1/templates`);
            const response = await fetch(`${this.apiEndpoint}/api/v1/templates`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('Template data:', data);
            
            this.templates = data.templates || [];
            console.log('Loaded templates:', this.templates);
            
            this.renderTemplateSelect();
            this.updateStatus(`${window.i18n ? 'Successfully loaded' : 'Successfully loaded'} ${this.templates.length} ${window.i18n ? 'templates' : 'templates'}`);
        } catch (error) {
            console.error('Failed to load templates:', error);
            this.updateStatus(window.i18n ? window.i18n.t('errorLoadingTemplates') : 'Failed to load templates, using default templates', 'error');
            // Use default templates
            this.templates = ['default', 'modern-card', 'glassmorphism', 'minimalist'];
            this.renderTemplateSelect();
        }
    }

    renderTemplateSelect() {
        const select = document.getElementById('templateSelect');
        console.log('Rendering template dropdown, template count:', this.templates.length);
        
        // Clear existing options
        select.innerHTML = '';

        if (this.templates.length === 0) {
            select.innerHTML = `<option value="">${window.i18n ? 'No templates available' : 'No templates available'}</option>`;
            return;
        }

        this.templates.forEach(template => {
            console.log('Creating template option:', template);
            const option = document.createElement('option');
            option.value = template;
            option.textContent = this.formatTemplateName(template);
            
            // If this is the currently selected template, set it as selected
            if (template === this.currentTemplate) {
                option.selected = true;
            }
            
            select.appendChild(option);
        });
    }

    formatTemplateName(template) {
        return template.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    selectTemplate(template) {
        this.currentTemplate = template;
        
        // 更新下拉框选中状态
        const select = document.getElementById('templateSelect');
        if (select) {
            select.value = template;
        }
        
        // 更新当前模板显示
        const currentTemplateSpan = document.getElementById('currentTemplate');
        if (currentTemplateSpan) {
            currentTemplateSpan.textContent = template;
        }
        
        // 加载模板内容到编辑器
        this.loadTemplateContent(template);
        
        // 更新预览
        this.updatePreview();
    }

    async loadTemplateContent(template) {
        try {
            const response = await fetch(`${this.apiEndpoint}/api/v1/templates/${template}`);
            const data = await response.json();
            
            if (data.content) {
                document.getElementById('svgEditor').value = data.content;
            }
            
        } catch (error) {
            console.error('Failed to load template content:', error);
            this.updateStatus(window.i18n ? window.i18n.t('errorApplyingTemplate') : 'Failed to load template content', 'error');
        }
    }

    async updatePreview() {
        const previewContainer = document.getElementById('svgPreview');
        previewContainer.innerHTML = '<div class="loading"></div>';

        try {
            const params = new URLSearchParams({
                template: this.currentTemplate
            });

            const response = await fetch(`${this.apiEndpoint}/now-playing.svg?${params}`);
            const svgContent = await response.text();
            
            // 清空容器并插入SVG
            previewContainer.innerHTML = '';
            
            // 创建一个临时容器来解析SVG
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = svgContent;
            const svgElement = tempDiv.querySelector('svg');
            
            if (svgElement) {
                previewContainer.appendChild(svgElement);
            } else {
                previewContainer.innerHTML = svgContent;
            }
            
            this.updateStatus(window.i18n ? 'Preview updated' : 'Preview updated');
            
        } catch (error) {
            console.error('Failed to update preview:', error);
            previewContainer.innerHTML = `
                <div class="error" style="
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    width: 100%;
                    height: 120px;
                    color: #f85149;
                    font-size: 14px;
                    background: transparent;
                    text-align: center;
                    border-radius: 8px;
                ">
                    <div>
                        <p style="margin: 0 0 8px 0;">${window.i18n ? 'Failed to update preview' : 'Failed to update preview'}</p>
                        <small style="opacity: 0.7;">${error.message}</small>
                    </div>
                </div>
            `;
            this.updateStatus(window.i18n ? 'Preview update failed' : 'Preview update failed', 'error');
        }
    }

    resetTemplate() {
        this.loadTemplateContent(this.currentTemplate);
        this.updateStatus(window.i18n ? window.i18n.t('templateReset') : 'Template reset');
    }

    exportSvg() {
        const svgContent = document.getElementById('svgPreview').innerHTML;
        const blob = new Blob([svgContent], { type: 'image/svg+xml' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `now-playing-${this.currentTemplate}.svg`;
        a.click();
        
        URL.revokeObjectURL(url);
        this.updateStatus(window.i18n ? window.i18n.t('svgExported') : 'SVG exported');
    }

    saveTemplate() {
        const customSvg = document.getElementById('svgEditor').value;
        const templateName = prompt(window.i18n ? 'Enter template name:' : 'Enter template name:', `custom-${Date.now()}`);
        
        if (templateName) {
            // Save to local storage
            const savedTemplates = JSON.parse(localStorage.getItem('customTemplates') || '{}');
            savedTemplates[templateName] = customSvg;
            localStorage.setItem('customTemplates', JSON.stringify(savedTemplates));
            
            this.updateStatus(`${window.i18n ? 'Template' : 'Template'} "${templateName}" ${window.i18n ? 'saved' : 'saved'}`);
        }
    }

    openSettings() {
        document.getElementById('settingsModal').style.display = 'block';
        
        // 加载当前设置
        document.getElementById('apiEndpoint').value = this.apiEndpoint;
        document.getElementById('refreshInterval').value = this.settings.refreshInterval;
        document.getElementById('autoRefresh').checked = this.settings.autoRefresh;
        document.getElementById('showGrid').checked = this.settings.showGrid;
    }

    closeModal(modalId) {
        document.getElementById(modalId).style.display = 'none';
    }

    saveSettings() {
        this.apiEndpoint = document.getElementById('apiEndpoint').value;
        this.settings.refreshInterval = parseInt(document.getElementById('refreshInterval').value);
        this.settings.autoRefresh = document.getElementById('autoRefresh').checked;
        this.settings.showGrid = document.getElementById('showGrid').checked;
        
        localStorage.setItem('nowPlayingSettings', JSON.stringify({
            apiEndpoint: this.apiEndpoint,
            ...this.settings
        }));
        
        this.applySettings();
        this.closeModal('settingsModal');
        this.updateStatus(window.i18n ? window.i18n.t('settingsSaved') : 'Settings saved');
    }

    resetSettings() {
        this.apiEndpoint = 'http://localhost:8000';
        this.settings = {
            autoRefresh: true,
            refreshInterval: 5,
            showGrid: false
        };
        
        localStorage.removeItem('nowPlayingSettings');
        this.applySettings();
        this.updateStatus(window.i18n ? window.i18n.t('settingsReset') : 'Settings reset');
    }

    loadSettings() {
        const saved = localStorage.getItem('nowPlayingSettings');
        if (saved) {
            const settings = JSON.parse(saved);
            this.apiEndpoint = settings.apiEndpoint || 'http://localhost:8000';
            this.settings = { ...this.settings, ...settings };
        }
        this.applySettings();
    }

    applySettings() {
        // 应用网格显示
        const previewContainer = document.querySelector('.preview-container');
        if (this.settings.showGrid) {
            previewContainer.classList.add('grid-overlay');
        } else {
            previewContainer.classList.remove('grid-overlay');
        }

        // 应用自动刷新
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
        }

        if (this.settings.autoRefresh) {
            this.autoRefreshInterval = setInterval(() => {
                this.updatePreview();
            }, this.settings.refreshInterval * 1000);
        }
    }

    updateStatus(message, type = 'info') {
        const statusElement = document.getElementById('statusText');
        if (statusElement) {
            statusElement.textContent = message;
            statusElement.className = type;
            
            // Clear status after 3 seconds
            setTimeout(() => {
                statusElement.textContent = window.i18n ? window.i18n.t('ready') : 'Ready';
                statusElement.className = '';
            }, 3000);
        }
    }

    escapeHtml(html) {
        const div = document.createElement('div');
        div.textContent = html;
        return div.innerHTML;
    }

    applyCustomSvg() {
        const customSvg = document.getElementById('svgEditor').value;
        const previewContainer = document.getElementById('svgPreview');
        
        try {
            // 清空容器
            previewContainer.innerHTML = '';
            
            // 创建一个临时容器来解析SVG
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = customSvg;
            const svgElement = tempDiv.querySelector('svg');
            
            if (svgElement) {
                previewContainer.appendChild(svgElement);
            } else {
                previewContainer.innerHTML = customSvg;
            }
            
            this.updateStatus(window.i18n ? 'Custom SVG applied' : 'Custom SVG applied');
        } catch (error) {
            previewContainer.innerHTML = `
                <div style="
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    width: 100%;
                    height: 120px;
                    color: #f85149;
                    font-size: 14px;
                    background: transparent;
                    text-align: center;
                ">
                    <div>
                        <p style="margin: 0;">${window.i18n ? 'SVG format error' : 'SVG format error'}</p>
                        <small style="opacity: 0.7;">${error.message}</small>
                    </div>
                </div>
            `;
            this.updateStatus(window.i18n ? 'SVG format error' : 'SVG format error', 'error');
        }
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new NowPlayingEditor();
});

// 键盘快捷键
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
            case 's':
                e.preventDefault();
                document.getElementById('saveTemplate').click();
                break;
            case 'r':
                e.preventDefault();
                document.getElementById('refreshPreview').click();
                break;
            case 'e':
                e.preventDefault();
                document.getElementById('exportSvg').click();
                break;
        }
    }
    
    if (e.key === 'Escape') {
        // 关闭所有模态框
        document.querySelectorAll('.modal').forEach(modal => {
            modal.style.display = 'none';
        });
    }
});
