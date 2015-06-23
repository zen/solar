$ () ->
  connections = {}
  connections_simplified = {}

  cy = init_main_graph()
  cy_edge_preview = init_edge_preview_graph()
  connections_promise = load_connections()
  connections_promise.then (data) ->
    connections = data

    tmp = {}

    for e in connections.edges
      tmp["#{e.data.source}->#{e.data.target}"] = e

    connections_simplified = {
      nodes: connections.nodes,
      edges: (e for k, e of tmp)
    }

    cy.batch () ->
      cy.add {group: 'nodes', data: node.data} for node in connections_simplified.nodes
      cy.add {group: 'edges', data: edge.data} for edge in connections_simplified.edges

  cy.on 'tap', (ev) ->
    el = ev.cyTarget

    return unless (el.length || el.isEdge?())

    nodes = el.connectedNodes()
    node_formatter = (node, left) -> {group: 'nodes', data: {id: node.id()}, position: {x: left, y: 125}}
    cy_edge_preview.batch () ->
      cy_edge_preview.remove('')
      cy_edge_preview.add (node_formatter nodes[0], 100)
      cy_edge_preview.add (node_formatter nodes[1], 600)
      for e in connections.edges
        if e.data.source == nodes[0].id() && e.data.target == nodes[1].id()
          cy_edge_preview.add {group: 'edges', data: e.data}

      cy_edge_preview.resize()


load_connections = () ->
  connections = $.Deferred()
  connections_get = $.get '/connections.json',
    ((data) ->
      console.log 'data', data
      ret ={
        nodes: ({data: node} for node in data.nodes),
        edges: ({data: edge} for edge in data.edges)
      }
      console.log ret
      connections.resolve(ret)
    ), 'json'

  connections


init_main_graph = () ->
  edge_line_color = '#F2B1BA'

  cy = cytoscape {
    container: $('#cy')[0],
    style: cytoscape.stylesheet().selector('node').css({
      'background-color': '#B3767E',
      content: 'data(id)'
    }).selector('edge').css({
      'line-color': edge_line_color,
      'target-arrow-color': '#000',
      'target-arrow-shape': 'triangle',
      width: 2,
      opacity: 0.8,
    #content: 'data(label)'
    }),
    ready: () -> console.log('ready'),
  #layout: {name: 'breadthfirst', fit: true},
  #layout: {name: 'concentric', levelWidth: ((node) -> 1)},
  #layout: {name: 'cose', animate: false, idealEdgeLength: 50},
    layout: {name: 'spread', maxExpandIterations: 10}
  }
  cy.edgehandles()

  cy.on 'select', (ev) ->
    cy.$().css({'line-color': edge_line_color})
    iid = ev.cyTarget.id()
    cy.$("edge[source=\"#{ iid }\"]").css({'line-color': '#000'})
    cy.$("edge[target=\"#{ iid }\"]").css({'line-color': '#00F'})

  cy.on 'tap', (ev) ->
    el = ev.cyTarget
    return if el.length
    cy.add {
      group: 'nodes',
      data: {id: 'x'},
      position: ev.cyPosition
    }

  cy.on 'mouseover', (ev) ->
    el = ev.cyTarget
    return unless (el.length || el.isNode?())
    el.css({'line-color': '#F00'})

  cy.on 'mouseout', (ev) ->
    el = ev.cyTarget
    return unless (el.length || el.isNode?())
    el.css({'line-color': edge_line_color})

  cy


init_edge_preview_graph = () ->
  edge_line_color = '#F2B1BA'
  cy = cytoscape {
    container: $('#cy-edge-preview')[0],
    style: cytoscape.stylesheet().selector('node').css({
      'background-color': '#B3767E',
      content: 'data(id)'
    }).selector('edge').css({
      'line-color': edge_line_color,
      'target-arrow-color': '#000',
      'target-arrow-shape': 'triangle',
      width: 2,
      opacity: 0.8,
      content: 'data(label)',
    }),
    ready: () -> console.log('ready'),
    layout: {name: 'spread', maxExpandIterations: 10}
  }

  cy

