// 古诗词网站 JavaScript

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    console.log('诗词雅集 - 页面加载完成');
    
    // 添加平滑滚动
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // 搜索框自动聚焦（仅在搜索页面）
    const searchInput = document.querySelector('.search-form-large input');
    if (searchInput && !searchInput.value) {
        searchInput.focus();
    }
});

// 随机诗词 API 调用示例
async function getRandomPoem() {
    try {
        const response = await fetch('/api/poems/random');
        const data = await response.json();
        if (data.success) {
            return data.data;
        }
    } catch (error) {
        console.error('获取随机诗词失败:', error);
    }
    return null;
}

// 搜索 API 调用示例
async function searchPoems(keyword, limit = 20) {
    try {
        const response = await fetch(`/api/poems/search?q=${encodeURIComponent(keyword)}&limit=${limit}`);
        const data = await response.json();
        if (data.success) {
            return data.data;
        }
    } catch (error) {
        console.error('搜索失败:', error);
    }
    return [];
}
