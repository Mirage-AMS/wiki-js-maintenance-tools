<script>
document.addEventListener('DOMContentLoaded', function() {
    // 全局变量
    let currentPage = 1;
    const cardsPerPage = 8;
    let cardData = [];
    let filteredCards = [];
    let filterOptions = {
        levels: new Set(),
        types: new Set(),
        attributes: new Set()
    };
    let allFilterValues = {
        levels: new Set(),
        types: new Set(),
        attributes: new Set()
    };

    // DOM 元素
    const cardContainer = document.getElementById('card-container');
    const pageNumbersContainer = document.getElementById('page-numbers');
    const prevPageBtn = document.getElementById('prev-page');
    const nextPageBtn = document.getElementById('next-page');
    const filterToggle = document.getElementById('filter-toggle');
    const filtersContainer = document.getElementById('filters-container');
    const filterGroups = document.querySelector('.filter-groups');
    const clearFiltersBtn = document.getElementById('clear-filters');
    const filterCount = document.getElementById('filter-count');

    // 初始化
    loadCardData();

    // 事件监听器
    prevPageBtn.addEventListener('click', goToPrevPage);
    nextPageBtn.addEventListener('click', goToNextPage);
    filterToggle.addEventListener('click', toggleFilters);
    clearFiltersBtn.addEventListener('click', clearAllFilters);

    // 从JSON文件加载数据
    function loadCardData() {
        cardContainer.innerHTML = '<p class="loading">加载卡牌数据中...</p>';

        fetch('/assets/intelligence.json')
            .then(response => {
                if (!response.ok) throw new Error('网络响应不正常');
                return response.json();
            })
            .then(data => {
                cardData = data;
                filteredCards = [...cardData];
                extractFilterValues();
                renderFilterOptions();
                renderCards();
                renderPagination();
                updateFilterCount();
            })
            .catch(error => {
                console.error('加载数据时出错:', error);
                cardContainer.innerHTML = '<p class="error">加载卡牌数据失败，请稍后重试</p>';
            });
    }

    // 提取所有筛选选项值（支持数组类型）
    function extractFilterValues() {
        cardData.forEach(card => {
            // 处理等级（字符串）
            allFilterValues.levels.add(card.level);

            // 处理类型（数组）
            if (Array.isArray(card.type)) {
                card.type.forEach(type => allFilterValues.types.add(type));
            } else {
                allFilterValues.types.add(card.type);
            }

            // 处理属性（数组）
            if (Array.isArray(card.attribute) && card.attribute.length > 0) {
                card.attribute.forEach(attr => allFilterValues.attributes.add(attr));
            }
        });
    }

    // 创建筛选组
    function createFilterGroup(label, type, values, displayFn) {
        const group = document.createElement('div');
        group.className = 'filter-group';

        const groupLabel = document.createElement('label');
        groupLabel.className = 'filter-group-label';
        groupLabel.textContent = label;
        group.appendChild(groupLabel);

        const optionsContainer = document.createElement('div');
        optionsContainer.className = 'filter-options';

        values.forEach(value => {
            const option = document.createElement('label');
            option.className = 'filter-option';
            option.innerHTML = `
                <input type="checkbox" name="${type}" value="${value}">
                <span>${displayFn(value)}</span>
            `;

            const checkbox = option.querySelector('input');
            // 保持筛选状态
            if (filterOptions[type].has(value)) {
                checkbox.checked = true;
            }

            checkbox.addEventListener('change', (e) => {
                handleFilterChange(type, e.target.value, e.target.checked);
            });

            optionsContainer.appendChild(option);
        });

        group.appendChild(optionsContainer);
        return group;
    }

    // 渲染筛选选项
    function renderFilterOptions() {
        filterGroups.innerHTML = '';

        // 等级筛选（排序）
        const levelGroup = createFilterGroup(
            '卡牌等级',
            'levels',
            Array.from(allFilterValues.levels).sort((a, b) => {
                // 按低级、中级、高级、传奇排序
                const order = { '低级': 1, '中级': 2, '高级': 3, '传奇': 4};
                return order[a] - order[b];
            }),
            (value) => value
        );
        filterGroups.appendChild(levelGroup);

        // 类型筛选
        const typeGroup = createFilterGroup(
            '卡牌类型',
            'types',
            Array.from(allFilterValues.types).sort(),
            (value) => value
        );
        filterGroups.appendChild(typeGroup);

        // 属性筛选
        const attributeGroup = createFilterGroup(
            '卡牌属性',
            'attributes',
            Array.from(allFilterValues.attributes).sort(),
            (value) => value
        );
        filterGroups.appendChild(attributeGroup);
    }

    // 处理筛选变化
    function handleFilterChange(type, value, checked) {
        if (checked) {
            filterOptions[type].add(value);
        } else {
            filterOptions[type].delete(value);
        }

        applyFilters();
        updateFilterCount();
    }

    // 应用筛选条件（支持多类型/属性匹配）
    function applyFilters() {
        filteredCards = cardData.filter(card => {
            // 等级匹配
            const levelMatch = filterOptions.levels.size === 0 ||
                              filterOptions.levels.has(card.level);

            // 类型匹配（支持数组）
            const typeMatch = filterOptions.types.size === 0 ||
                             (Array.isArray(card.type)
                                ? card.type.some(t => filterOptions.types.has(t))
                                : filterOptions.types.has(card.type));

            // 属性匹配（支持数组和空数组）
            const attributeMatch = filterOptions.attributes.size === 0 ||
                                  (Array.isArray(card.attribute) &&
                                   card.attribute.some(a => filterOptions.attributes.has(a)));

            return levelMatch && typeMatch && attributeMatch;
        });

        currentPage = 1;
        renderCards();
        renderPagination();
    }

    // 清除所有筛选
    function clearAllFilters() {
        filterOptions = {
            levels: new Set(),
            types: new Set(),
            attributes: new Set()
        };

        document.querySelectorAll('.filter-option input:checked').forEach(checkbox => {
            checkbox.checked = false;
        });

        applyFilters();
        updateFilterCount();
    }

    // 更新筛选计数
    function updateFilterCount() {
        const totalFilters = filterOptions.levels.size +
                            filterOptions.types.size +
                            filterOptions.attributes.size;
        filterCount.textContent = `(${totalFilters})`;
    }

    // 切换筛选面板
    function toggleFilters() {
        filtersContainer.classList.toggle('filters-visible');
    }

    // 渲染卡牌（优化多类型/属性展示）
    function renderCards() {
        cardContainer.innerHTML = '';

        const startIndex = (currentPage - 1) * cardsPerPage;
        const endIndex = startIndex + cardsPerPage;
        const currentCards = filteredCards.slice(startIndex, endIndex);

        if (currentCards.length === 0) {
            cardContainer.innerHTML = '<p class="no-cards">没有找到符合条件的卡牌</p>';
            return;
        }

        currentCards.forEach(card => {
            const cardElement = document.createElement('div');
            cardElement.className = 'card';

            // 处理多类型展示（保持不变）
            const typesHtml = Array.isArray(card.type)
                ? card.type.map(type => `<span class="card-type">${type}</span>`).join('')
                : `<span class="card-type">${card.type}</span>`;

            // 处理多属性展示（保持不变，但后续会放入 badges 容器）
            const attributesHtml = Array.isArray(card.attribute) && card.attribute.length > 0
                ? card.attribute.map(attr => `
                    <div class="card-attribute attribute-${attr.toLowerCase()}"></div>
                  `).join('')
                : '';

            // 核心修改：将属性图标放入 .card-badges 容器，与等级分工定位
            cardElement.innerHTML = `
                <div class="card-image">
                    <img src="${card.image}" alt="${card.name}">
                    <!-- 等级：右上角（原逻辑保留） -->
                    <div class="card-level level-${card.level.toLowerCase()}">${card.level}</div>
                    <!-- 属性图标：左上角（用 .card-badges 统一包裹，方便横向排列） -->
                    <div class="card-badges">${attributesHtml}</div>
                </div>
                <div class="card-info">
                    <h3 class="card-name">${card.name}</h3>
                    <!-- 原代码中是 .card-types，此处匹配 CSS 中的 .card-meta（避免样式失效） -->
                    <div class="card-meta">${typesHtml}</div>
                </div>
            `;

            cardElement.addEventListener('click', () => {
                window.location.href = card.url;
            });

            cardContainer.appendChild(cardElement);
        });
    }

    // 渲染分页
    function renderPagination() {
        pageNumbersContainer.innerHTML = '';

        const totalPages = Math.ceil(filteredCards.length / cardsPerPage);

        prevPageBtn.disabled = currentPage === 1;
        nextPageBtn.disabled = currentPage === totalPages || totalPages === 0;

        // 优化页码显示逻辑
        for (let i = 1; i <= totalPages; i++) {
            // 始终显示第一页、最后一页和当前页附近的页码
            if (i === 1 || i === totalPages || Math.abs(i - currentPage) <= 1) {
                const pageNumber = document.createElement('div');
                pageNumber.className = `page-number ${i === currentPage ? 'active' : ''}`;
                pageNumber.textContent = i;
                pageNumber.addEventListener('click', () => goToPage(i));
                pageNumbersContainer.appendChild(pageNumber);
            } else if (
                (i === 2 && currentPage > 3) ||
                (i === totalPages - 1 && currentPage < totalPages - 2)
            ) {
                // 只在必要时显示省略号
                const ellipsis = document.createElement('div');
                ellipsis.className = 'page-number ellipsis';
                ellipsis.textContent = '...';
                ellipsis.style.pointerEvents = 'none';

                // 避免重复添加省略号
                const lastChild = pageNumbersContainer.lastChild;
                if (!lastChild || lastChild.textContent !== '...') {
                    pageNumbersContainer.appendChild(ellipsis);
                }
            }
        }
    }

    // 页面导航
    function goToPage(page) {
        currentPage = page;
        renderCards();
        renderPagination();
        scrollToTop();
    }

    function goToPrevPage() {
        if (currentPage > 1) {
            goToPage(currentPage - 1);
        }
    }

    function goToNextPage() {
        const totalPages = Math.ceil(filteredCards.length / cardsPerPage);
        if (currentPage < totalPages) {
            goToPage(currentPage + 1);
        }
    }

    // 滚动到顶部
    function scrollToTop() {
        const catalog = document.getElementById('card-catalog');
        catalog.scrollIntoView({ behavior: 'smooth' });
    }
});
</script>