document.addEventListener('DOMContentLoaded', () => //only after html is loaded: no access before elements exist
{
    // ui 
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {//enable switching between parsing techniques
            
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
           
            btn.classList.add('active');
            const target = btn.getAttribute('data-target');
            document.getElementById(target).classList.add('active');
        });
    });

    // main part
    const btnParse = document.getElementById('btn-parse');
    const spinner = document.getElementById('loading-spinner');
    const globalError = document.getElementById('global-error');

    btnParse.addEventListener('click', async () => {//user input
        const grammarStr = document.getElementById('grammar-input').value;
        const inputStr = document.getElementById('string-input').value;

        if (!grammarStr || !inputStr) {//validation
            showError('Please provide both grammar rules and input string.');
            return;
        }

        hideError();
        spinner.classList.remove('hidden');//loading state when the data is getting input any button present gets diabled for a better visual and enhanced ui working
        btnParse.disabled = true;

        try {//api calling
            const response = await fetch('http://127.0.0.1:5000/api/parse', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ grammar: grammarStr, input: inputStr })
});

            const data = await response.json();

            if (data.error) {
                showError(data.error);
            } else {
                updateUI(data);
            }

        } catch (err) {
            showError('Failed to connect to the parsing server. Make sure backend is running.');
            console.error(err);
        } finally {
            spinner.classList.add('hidden');
            btnParse.disabled = false;
        }
    });

    function showError(msg) {
        globalError.textContent = msg;
        globalError.classList.remove('hidden');
    }

    function hideError() {
        globalError.classList.add('hidden');
    }


    function updateUI(data) {
        renderTokens(data.tokens);//upadte token table
        renderSets(data.sets);//upadte first follow sets
        
        // LL1
        if (data.ll1) {
            if (data.ll1.conflicts) {//ambiguity in the input
                document.getElementById('ll1-error').textContent = data.ll1.conflict_details.join(' | ');
                document.getElementById('ll1-error').classList.remove('hidden');
            } else {
                document.getElementById('ll1-error').classList.add('hidden');
            }
            renderLL1Table(data.ll1.table, data.grammar.terminals, data.grammar.non_terminals);
            renderSimulation('ll1-sim-table', data.ll1.history);
            
            // Render LL1 Tree
            if (Object.keys(data.ll1.tree).length > 0 && typeof window.renderD3Tree === 'function') {
                window.renderD3Tree(data.ll1.tree, '#ll1-tree');//tree_visualization.js
            } else {
                document.getElementById('ll1-tree').innerHTML = '<div class="empty-state">No tree generated (parsing may have failed).</div>';
            }
        }

        // LR1
        if (data.lr1_collection) {
            renderLRStates('lr1-states-container', data.lr1_collection, 'LR(1) State');
        }

        // LALR States
        if (data.lalr_states) {
            renderLALRStates('lalr-states-container', data.lalr_states);
        }

        // LALR Table and Simulation
        if (data.lalr) {
            if (data.lalr.conflicts) {
                document.getElementById('lalr-error').textContent = data.lalr.conflict_details.join(' | ');
                document.getElementById('lalr-error').classList.remove('hidden');
            } else {
                document.getElementById('lalr-error').classList.add('hidden');
            }
            renderLALRTable(data.lalr.action_table, data.lalr.goto_table, data.grammar.terminals, data.grammar.non_terminals);
            renderSimulation('lalr-sim-table', data.lalr.history);
            
            // Render LALR Tree
            if (Object.keys(data.lalr.tree).length > 0 && typeof window.renderD3Tree === 'function') {
                window.renderD3Tree(data.lalr.tree, '#lalr-tree');
            } else {
                document.getElementById('lalr-tree').innerHTML = '<div class="empty-state">No tree generated (parsing may have failed).</div>';
            }
        }
    }

    function renderTokens(tokens) {//lexeme
        document.getElementById('token-count').textContent = `${tokens.length} Tokens`;
        const tbody = document.querySelector('#token-table tbody');
        tbody.innerHTML = '';
        
        if (tokens.length === 0) {
            tbody.innerHTML = '<tr><td colspan="2" class="empty-state">No tokens found</td></tr>';
            return;
        }

        tokens.forEach(t => {//rows
            const tr = document.createElement('tr');
            const clz = t.token === 'ERROR' ? 'style="color: var(--danger)"' : '';
            tr.innerHTML = `
                <td ${clz}>${escapeHtml(t.lexeme)}</td>
                <td><span class="badge">${t.token}</span></td>
            `;
            tbody.appendChild(tr);
        });
    }

    function renderSets(sets) {//first and follow
        const tbody = document.querySelector('#sets-table tbody');
        tbody.innerHTML = '';
        
        if (!sets || !sets.first) return;

        const nonTerminals = Object.keys(sets.first);
        nonTerminals.forEach(nt => {
            const tr = document.createElement('tr');
            const firstSet = sets.first[nt] ? sets.first[nt].join(', ') : '';
            const followSet = sets.follow[nt] ? sets.follow[nt].join(', ') : '';
            
            tr.innerHTML = `
                <td><strong>${escapeHtml(nt)}</strong></td>
                <td>{ ${escapeHtml(firstSet)} }</td>
                <td>{ ${escapeHtml(followSet)} }</td>
            `;
            tbody.appendChild(tr);
        });
    }

    function renderLL1Table(table, terminals, non_terminals) {
        const thead = document.querySelector('#ll1-table thead');
        const tbody = document.querySelector('#ll1-table tbody');
        thead.innerHTML = '';
        tbody.innerHTML = '';

        if (!table) return;

        // Header row
        const terms = Array.from(new Set([...terminals, '$'])).filter(t => t !== 'epsilon');
        let headerRow = '<tr><th>Non-Terminal</th>';
        terms.forEach(t => {
            headerRow += `<th>${escapeHtml(t)}</th>`;
        });
        headerRow += '</tr>';
        thead.innerHTML = headerRow;

        // Body rows
        non_terminals.forEach(nt => {
            let tr = `<tr><td><strong>${escapeHtml(nt)}</strong></td>`;
            terms.forEach(t => {
                const rule = table[nt] ? table[nt][t] : null;
                const cellContent = rule ? `${nt} &rarr; ${rule.join(' ')}` : '';
                tr += `<td>${escapeHtml(cellContent)}</td>`;
            });
            tr += '</tr>';
            tbody.innerHTML += tr;
        });
    }

    function renderLRStates(containerId, states, titlePrefix) {
        const container = document.getElementById(containerId);
        container.innerHTML = '';
        
        if (!states || states.length === 0) {
            container.innerHTML = '<div class="empty-state">No states available.</div>';
            return;
        }

        states.forEach(state => {
            const card = document.createElement('div');
            card.className = 'state-card';
            
            let html = `<div class="state-card-header">`;
            html += `<span>${titlePrefix} ${state.id}</span>`;
            if (state.merged_from && state.merged_from.length > 0) {
                html += `<span style="font-size:0.75rem; color: var(--text-secondary)">Merged: ${state.merged_from.join(', ')}</span>`;
            }
            html += `</div>`;
            
            state.items.forEach(item => {
                html += `<div class="state-item">${escapeHtml(item)}</div>`;
            });
            
            card.innerHTML = html;
            container.appendChild(card);
        });
    }

    function renderLALRStates(containerId, states) {
        renderLRStates(containerId, states, 'LALR State');
    }

    function renderLALRTable(actionTbl, gotoTbl, terminals, non_terminals) {
        const thead = document.querySelector('#lalr-table thead');
        const tbody = document.querySelector('#lalr-table tbody');
        thead.innerHTML = '';
        tbody.innerHTML = '';

        if (!actionTbl) return;

        const states = Object.keys(actionTbl).map(Number).sort((a,b)=>a-b);
        const actionTerms = Array.from(new Set([...terminals, '$'])).filter(t => t !== 'epsilon');
        const gotoNonTerms = non_terminals; // Usually omit augmented start

        // Header row
        let headerRow = '<tr><th rowspan="2">State</th>';
        headerRow += `<th colspan="${actionTerms.length}" style="text-align:center; border-left:1px solid var(--border)">ACTION</th>`;
        headerRow += `<th colspan="${gotoNonTerms.length}" style="text-align:center; border-left:1px solid var(--border)">GOTO</th></tr><tr>`;
        
        actionTerms.forEach(t => { headerRow += `<th style="border-left:1px dashed var(--border)">${escapeHtml(t)}</th>`; });
        gotoNonTerms.forEach(nt => { headerRow += `<th style="border-left:1px dashed var(--border); color:var(--primary-hover)">${escapeHtml(nt)}</th>`; });
        headerRow += '</tr>';
        thead.innerHTML = headerRow;

        // Body
        states.forEach(st => {
            let tr = `<tr><td><strong>${st}</strong></td>`;
            
            actionTerms.forEach(t => {
                const act = actionTbl[st][t] || '';
                tr += `<td style="border-left:1px dashed var(--border)">${escapeHtml(act)}</td>`;
            });
            
            gotoNonTerms.forEach(nt => {
                const gt = (gotoTbl[st] && gotoTbl[st][nt] !== undefined) ? gotoTbl[st][nt] : '';
                tr += `<td style="border-left:1px dashed var(--border); color:var(--primary-hover)">${gt}</td>`;
            });
            
            tr += '</tr>';
            tbody.innerHTML += tr;
        });
    }

    function renderSimulation(tableId, history) {//3 thing stack ,input and action
        const tbody = document.querySelector(`#${tableId} tbody`);
        tbody.innerHTML = '';

        if (!history || history.length === 0) {
            tbody.innerHTML = '<tr><td colspan="3" class="empty-state">No parsing history available (check conflicts)</td></tr>';
            return;
        }

        history.forEach(step => {
            const tr = document.createElement('tr');
            if (step.action.toLowerCase().includes('error')) {
                tr.style.background = 'rgba(239, 68, 68, 0.1)';
            } else if (step.action.toLowerCase().includes('accept')) {
                tr.style.background = 'rgba(16, 185, 129, 0.1)';
            }
            
            tr.innerHTML = `
                <td>${escapeHtml(step.stack.join(' '))}</td>
                <td>${escapeHtml(step.input.join(' '))}</td>
                <td><strong>${escapeHtml(step.action)}</strong></td>
            `;
            tbody.appendChild(tr);
        });
    }

    function escapeHtml(unsafe) {
        return (unsafe || '').toString()
             .replace(/&/g, "&amp;")
             .replace(/</g, "&lt;")
             .replace(/>/g, "&gt;")
             .replace(/"/g, "&quot;")
             .replace(/'/g, "&#039;");
    }
});
