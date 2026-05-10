window.renderD3Tree = function(treeData, containerSelector) {
    const container = d3.select(containerSelector);
    container.selectAll("*").remove(); // Clear previous tree

    if (!treeData || !treeData.name) //validation:no trees{
        container.html('<div class="empty-state">No tree data to display.</div>');
        return;
    }

    // new visuals
    let { width, height } = container.node().getBoundingClientRect();
    if (width === 0) width = 800;
    if (height === 0) height = 500;

    const margin = { top: 50, right: 90, bottom: 50, left: 90 };
    
    // Create SVG and add Zoom capabilities
    const svg = container.append("svg")
        .attr("width", "100%")
        .attr("height", "100%")
        .call(d3.zoom().on("zoom", function (event) {
            svgGroup.attr("transform", event.transform);
        }))
        .on("dblclick.zoom", null);

    const svgGroup = svg.append("g")//container for all nodes and edges
        .attr("transform", `translate(${margin.left}, ${margin.top})`);

    // Construct a tree layout
    const treemap = d3.tree().nodeSize([60, 90]);//vertical & horizontal spacing
    
    let root = d3.hierarchy(treeData, function(d) { return d.children; });
    root.x0 = width / 2;
    root.y0 = 0;

    let i = 0;
    const duration = 1200; // Slowed down from 500ms for better comprehension

    // Collapse function to hide all children initially
    function collapseAll(d) {
        if (d.children) {
            d._children = d.children;
            d._children.forEach(collapseAll);
            d.children = null;
        }
    }

    if (root.children) {
        root._children = root.children;
        root._children.forEach(collapseAll);
        root.children = null;
    }

    update(root);

    // step by step expansion
    function unfoldNextLevel(nodes) {
        let nextNodes = [];
        nodes.forEach(d => {
            if (d._children) {
                d.children = d._children;
                d._children = null;
                nextNodes.push(...d.children);
            }
        });
        
        if (nextNodes.length > 0) {
            update(root); // Update with root so it renders all new children
            setTimeout(() => {
                unfoldNextLevel(nextNodes);
            }, duration + 400); // Wait for transition + 400ms pause
        }
    }

    // Start unfolding animation after initial render
    setTimeout(() => {
        unfoldNextLevel([root]);
    }, duration + 100);

    // Initial centering animation
    setTimeout(() => {
        const bounds = container.node().getBoundingClientRect();
        const cw = bounds.width || width;
        const zoom = d3.zoom().on("zoom", function (event) {
            svgGroup.attr("transform", event.transform);
        });
        svg.transition()
           .duration(750)
           .call(zoom.transform, d3.zoomIdentity.translate(cw / 2, margin.top).scale(1));
    }, 100);

    function update(source) //link and node creation,transitions
    {
        const treeDataMapped = treemap(root);
        const nodes = treeDataMapped.descendants();
        const links = treeDataMapped.descendants().slice(1);

        // Normalize vertical spacing
        nodes.forEach(d => { d.y = d.depth * 80 });

        const node = svgGroup.selectAll('g.node')
            .data(nodes, function(d) { return d.id || (d.id = ++i); });

        const nodeEnter = node.enter().append('g')
            .attr('class', function(d) { return "node" + (d.children || d._children ? " node--internal" : " node--leaf"); })
            .attr("transform", function(d) {
                const initX = d.parent ? d.parent.x0 : source.x0;
                const initY = d.parent ? d.parent.y0 : source.y0;
                return "translate(" + initX + "," + initY + ")";
            })
            .on('click', click);

        nodeEnter.append('circle')//node creation: circle means node for shape
            .attr('class', 'node')
            .attr('r', 1e-6);

        nodeEnter.append('text')//node creation-> text means the variables
            .attr("dy", ".35em")
            .text(function(d) { return d.data.name; })
            .style("fill-opacity", 1e-6);

        const nodeUpdate = nodeEnter.merge(node);

        nodeUpdate.transition()
            .duration(duration)
            .attr("transform", function(d) { 
                return "translate(" + d.x + "," + d.y + ")";
            });

        nodeUpdate.select('circle.node')
            .attr('r', 20)//nnode size
            .style("fill", function(d) //colour
            {
                return d._children ? "rgba(139, 92, 246, 0.3)" : null;
            })
            .style("stroke-width", function(d) {
                return d._children ? "3px" : "2px";
            });

        nodeUpdate.select('text')
            .transition()
            .duration(duration)
            .style("fill-opacity", 1);

        const nodeExit = node.exit().transition()
            .duration(duration)
            .attr("transform", function(d) {
                return "translate(" + source.x + "," + source.y + ")";
            })
            .remove();

        nodeExit.select('circle')
            .attr('r', 1e-6);

        nodeExit.select('text')
            .style("fill-opacity", 1e-6);

        const link = svgGroup.selectAll('path.link')
            .data(links, function(d) { return d.id; });

        const linkEnter = link.enter().insert('path', "g")
            .attr("class", "link")
            .attr('d', function(d) {
                const initX = d.parent ? d.parent.x0 : source.x0;
                const initY = d.parent ? d.parent.y0 : source.y0;
                const o = {x: initX, y: initY};
                return diagonal(o, o);
            });

        const linkUpdate = linkEnter.merge(link);

        linkUpdate.transition()
            .duration(duration)
            .attr('d', function(d){ return diagonal(d, d.parent) });

        link.exit().transition()
            .duration(duration)
            .attr('d', function(d) {
                const o = {x: source.x, y: source.y};
                return diagonal(o, o);
            })
            .remove();

        nodes.forEach(function(d) {
            d.x0 = d.x;
            d.y0 = d.y;
        });

        function diagonal(s, d) //edges
        {
            return `M ${s.x} ${s.y}
                    C ${s.x} ${(s.y + d.y) / 2},
                      ${d.x} ${(s.y + d.y) / 2},
                      ${d.x} ${d.y}`;
        }

        function click(event, d)//expand, collapse
         {
            if (d.children) {
                d._children = d.children;
                d.children = null;
            } else {
                d.children = d._children;
                d._children = null;
            }
            update(d);
        }
    }
};
