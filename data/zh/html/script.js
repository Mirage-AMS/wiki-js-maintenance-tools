<script>
// 等待DOM加载完成
document.addEventListener('DOMContentLoaded', function() {
  // 获取DOM元素
  const searchForm = document.getElementById('search-form');
  const searchInput = document.getElementById('search-input');
  const searchHeader = document.querySelector('.search-header');
  const resultsContainer = document.getElementById('results-container');
  const resultsList = document.getElementById('results-list');
  const resultsCount = document.getElementById('results-count');
  const prevPageBtn = document.getElementById('prev-page');
  const nextPageBtn = document.getElementById('next-page');
  const pageInfo = document.getElementById('page-info');
  const headerPlaceholder = document.getElementById('header-placeholder');
  
  // 搜索状态变量
  let currentPage = 1;
  const resultsPerPage = 10;
  let totalResults = 0;
  let allResults = [];
  let currentQuery = '';
  let headerHeight = 0;
  
  // 初始化 - 计算搜索头部高度用于占位
  setTimeout(() => {
    headerHeight = searchHeader.offsetHeight;
    headerPlaceholder.style.height = `${headerHeight}px`;
  }, 100);
  
  // 监听滚动事件，实现搜索框固定效果
  window.addEventListener('scroll', function() {
    const header = document.querySelector('.search-header');
    const placeholder = document.getElementById('header-placeholder');

    if (window.scrollY > 100) { // 滚动超过100px时固定
      header.classList.add('sticky', 'active');
      placeholder.style.display = 'block';
      placeholder.style.height = header.offsetHeight + 'px';
    } else {
      header.classList.remove('sticky', 'active');
      placeholder.style.display = 'none';
      placeholder.style.height = '0';
    }
  });

  // 表单提交处理
  searchForm.addEventListener('submit', function(e) {
    e.preventDefault();
    const query = searchInput.value.trim();
    
    if (query) {
      performSearch(query);
    }
  });
  
  // 分页按钮事件
  prevPageBtn.addEventListener('click', function() {
    if (currentPage > 1) {
      currentPage--;
      displayResults();
      // 滚动到结果顶部
      resultsContainer.scrollIntoView({ behavior: 'smooth' });
    }
  });
  
  nextPageBtn.addEventListener('click', function() {
    if (currentPage < getTotalPages()) {
      currentPage++;
      displayResults();
      // 滚动到结果顶部
      resultsContainer.scrollIntoView({ behavior: 'smooth' });
    }
  });
  
  // 执行搜索
  function performSearch(query) {
    currentQuery = query;
    currentPage = 1;
    
    // 显示加载状态
    resultsList.innerHTML = '<li class="loading">搜索中...</li>';
    resultsContainer.classList.remove('hidden');
    searchHeader.classList.add('active');
    
    // 触发一次滚动检查以确保样式正确
    window.dispatchEvent(new Event('scroll'));
    
    // 模拟搜索结果
    setTimeout(() => {
      fetchWikiData(query).then(results => {
        allResults = results;
        totalResults = results.length;
        resultsCount.textContent = totalResults;
        displayResults();
      });
    }, 600);
  }
  
  // 显示当前页结果
  function displayResults() {
    resultsList.innerHTML = '';
    
    const startIndex = (currentPage - 1) * resultsPerPage;
    const endIndex = Math.min(startIndex + resultsPerPage, allResults.length);
    const currentResults = allResults.slice(startIndex, endIndex);
    
    if (currentResults.length === 0) {
      resultsList.innerHTML = '<li class="no-results">没有找到匹配的结果</li>';
    } else {
      currentResults.forEach(result => {
        const li = document.createElement('li');
        li.className = 'result-item';
        
        li.innerHTML = `
          <div class="result-image-container">
            <img src="${result.imageUrl}" 
                 alt="${result.title}的卡牌图片" 
                 class="result-image"
                 onerror="this.src='https://picsum.photos/seed/${result.id}/120/160'; this.alt='${result.title}的默认卡牌图片'">
          </div>
          <div class="result-content">
            <a href="${result.url}" class="result-title" target="_blank">${highlightMatch(result.title, currentQuery)}</a>
            <div class="result-link">${result.url}</div>
            <p class="result-snippet">${highlightMatch(result.snippet, currentQuery)}</p>
            
            ${result.properties ? `
              <div class="card-properties">
                ${Object.entries(result.properties).map(([key, value]) => `
                  <span class="property-tag">${key}: ${value}</span>
                `).join('')}
              </div>
            ` : ''}
          </div>
        `;
        
        resultsList.appendChild(li);
      });
    }
    
    updatePagination();
  }
  
  // 更新分页控件
  function updatePagination() {
    const totalPages = getTotalPages();
    
    pageInfo.textContent = `第 ${currentPage} 页，共 ${totalPages} 页`;
    prevPageBtn.disabled = currentPage === 1;
    nextPageBtn.disabled = currentPage === totalPages;
  }
  
  // 计算总页数
  function getTotalPages() {
    return Math.ceil(totalResults / resultsPerPage);
  }
  
  // 高亮匹配文本
  function highlightMatch(text, query) {
    if (!query) return text;
    const regex = new RegExp(`(${query})`, 'gi');
    return text.replace(regex, '<strong>$1</strong>');
  }
  
  // 模拟获取卡牌数据
  function fetchWikiData(query) {
    return new Promise(resolve => {
      const mockResults = [
        {
          id: 101,
          title: `${query} 卡牌介绍`,
          url: '/cards/' + query.toLowerCase().replace(/\s+/g, '-'),
          imageUrl: `https://picsum.photos/seed/${query}1/120/160`,
          snippet: `这是关于 ${query} 卡牌的详细介绍，包括其属性、技能和使用方法。`,
          properties: { "属性": "火", "稀有度": "SSR", "攻击力": "9500" }
        },
        {
          id: 102,
          title: `${query} 卡牌获取方式`,
          url: '/guides/how-to-get-' + query.toLowerCase().replace(/\s+/g, '-'),
          imageUrl: `https://picsum.photos/seed/${query}2/120/160`,
          snippet: `本文介绍了 ${query} 卡牌的多种获取途径。`,
          properties: { "获取难度": "中等", "推荐指数": "★★★★☆" }
        },
        {
          id: 103,
          title: `${query} 卡牌组合策略`,
          url: '/strategies/' + query.toLowerCase().replace(/\s+/g, '-') + '-combos',
          imageUrl: `https://picsum.photos/seed/${query}3/120/160`,
          snippet: `探索 ${query} 卡牌与其他卡牌的最佳组合方式。`,
          properties: { "最佳搭档": "水之精灵", "战术定位": "主攻" }
        }
      ];
      
      // 扩展结果用于测试分页
      const expandedResults = [];
      for (let i = 0; i < 5; i++) {
        mockResults.forEach(result => {
          expandedResults.push({
            ...result,
            id: result.id + i * 10,
            title: `${result.title} (变体 ${i+1})`,
            imageUrl: `https://picsum.photos/seed/${query}${result.id+i}/120/160`
          });
        });
      }
      
      resolve(expandedResults);
    });
  }
});

</script>