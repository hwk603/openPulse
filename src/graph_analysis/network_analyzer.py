"""
EasyGraph-based collaboration network analysis
"""
import easygraph as eg
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
from loguru import logger


class CollaborationNetworkAnalyzer:
    """Analyzer for developer collaboration networks using EasyGraph"""

    def __init__(self):
        self.graph: Optional[eg.Graph] = None

    def build_network(
        self, collaborations: List[Dict[str, Any]]
    ) -> eg.Graph:
        """
        Build collaboration network from collaboration data

        Args:
            collaborations: List of collaboration records with 'from', 'to', 'weight', 'timestamp'

        Returns:
            EasyGraph Graph object
        """
        self.graph = eg.Graph()

        for collab in collaborations:
            from_user = collab["from"]
            to_user = collab["to"]
            weight = collab.get("weight", 1.0)
            timestamp = collab.get("timestamp")

            # Add nodes if not exist
            if not self.graph.has_node(from_user):
                self.graph.add_node(from_user)
            if not self.graph.has_node(to_user):
                self.graph.add_node(to_user)

            # Add or update edge
            if self.graph.has_edge(from_user, to_user):
                # Update weight (accumulate)
                current_weight = self.graph[from_user][to_user].get("weight", 0)
                self.graph[from_user][to_user]["weight"] = current_weight + weight
            else:
                self.graph.add_edge(
                    from_user, to_user, weight=weight, timestamp=timestamp
                )

        logger.info(
            f"Built collaboration network with {self.graph.number_of_nodes()} nodes "
            f"and {self.graph.number_of_edges()} edges"
        )
        return self.graph

    def calculate_centrality_metrics(self) -> Dict[str, Dict[str, float]]:
        """
        Calculate various centrality metrics for all nodes

        Returns:
            Dictionary mapping node -> centrality metrics
        """
        if not self.graph:
            raise ValueError("Graph not initialized. Call build_network first.")

        logger.info("Calculating centrality metrics...")

        # Degree centrality
        degree_centrality = eg.degree_centrality(self.graph)

        # Betweenness centrality
        betweenness_centrality = eg.betweenness_centrality(self.graph)

        # Closeness centrality
        closeness_centrality = eg.closeness_centrality(self.graph)

        # PageRank
        try:
            pagerank = eg.pagerank(self.graph)
        except Exception as e:
            logger.warning(f"PageRank calculation failed: {e}")
            pagerank = {node: 0.0 for node in self.graph.nodes}

        # Combine all metrics
        centrality_metrics = {}
        for node in self.graph.nodes:
            centrality_metrics[node] = {
                "degree_centrality": degree_centrality.get(node, 0.0),
                "betweenness_centrality": betweenness_centrality.get(node, 0.0),
                "closeness_centrality": closeness_centrality.get(node, 0.0),
                "pagerank": pagerank.get(node, 0.0),
            }

        logger.info(f"Calculated centrality metrics for {len(centrality_metrics)} nodes")
        return centrality_metrics

    def detect_structural_holes(self) -> Dict[str, Any]:
        """
        Detect structural holes in the network

        Returns:
            Dictionary with structural hole metrics for each node
        """
        if not self.graph:
            raise ValueError("Graph not initialized. Call build_network first.")

        logger.info("Detecting structural holes...")

        structural_holes = {}

        try:
            # Constraint (Burt's constraint measure)
            # Lower constraint = more structural holes occupied
            constraint = eg.constraint(self.graph)

            # Effective size
            effective_size = eg.effective_size(self.graph)

            # Combine metrics
            for node in self.graph.nodes:
                structural_holes[node] = {
                    "constraint": constraint.get(node, 1.0),
                    "effective_size": effective_size.get(node, 0.0),
                    "is_bridge": constraint.get(node, 1.0) < 0.5,  # Low constraint = bridge
                }

            logger.info(f"Detected structural holes for {len(structural_holes)} nodes")

        except Exception as e:
            logger.error(f"Structural hole detection failed: {e}")
            # Fallback: use betweenness as proxy
            betweenness = eg.betweenness_centrality(self.graph)
            for node in self.graph.nodes:
                structural_holes[node] = {
                    "constraint": 1.0 - betweenness.get(node, 0.0),
                    "effective_size": betweenness.get(node, 0.0) * self.graph.degree(node),
                    "is_bridge": betweenness.get(node, 0.0) > 0.1,
                }

        return structural_holes

    def detect_communities(self) -> Dict[str, Any]:
        """
        Detect communities in the network

        Returns:
            Dictionary with community information
        """
        if not self.graph:
            raise ValueError("Graph not initialized. Call build_network first.")

        logger.info("Detecting communities...")

        try:
            # Louvain community detection
            communities = eg.louvain_communities(self.graph)

            # Convert to node -> community_id mapping
            node_to_community = {}
            for community_id, members in enumerate(communities):
                for node in members:
                    node_to_community[node] = community_id

            # Calculate modularity
            modularity = eg.modularity(self.graph, communities)

            result = {
                "communities": communities,
                "node_to_community": node_to_community,
                "num_communities": len(communities),
                "modularity": modularity,
            }

            logger.info(
                f"Detected {len(communities)} communities with modularity {modularity:.3f}"
            )
            return result

        except Exception as e:
            logger.error(f"Community detection failed: {e}")
            return {
                "communities": [],
                "node_to_community": {},
                "num_communities": 0,
                "modularity": 0.0,
            }

    def calculate_network_metrics(self) -> Dict[str, float]:
        """
        Calculate overall network metrics

        Returns:
            Dictionary with network-level metrics
        """
        if not self.graph:
            raise ValueError("Graph not initialized. Call build_network first.")

        logger.info("Calculating network metrics...")

        metrics = {
            "num_nodes": self.graph.number_of_nodes(),
            "num_edges": self.graph.number_of_edges(),
            "density": eg.density(self.graph),
            "average_degree": sum(dict(self.graph.degree()).values()) / self.graph.number_of_nodes()
            if self.graph.number_of_nodes() > 0
            else 0.0,
        }

        # Clustering coefficient
        try:
            metrics["average_clustering"] = eg.average_clustering(self.graph)
        except Exception as e:
            logger.warning(f"Clustering coefficient calculation failed: {e}")
            metrics["average_clustering"] = 0.0

        # Connected components
        try:
            components = list(eg.connected_components(self.graph))
            metrics["num_components"] = len(components)
            metrics["largest_component_size"] = max(len(c) for c in components) if components else 0
        except Exception as e:
            logger.warning(f"Connected components calculation failed: {e}")
            metrics["num_components"] = 0
            metrics["largest_component_size"] = 0

        logger.info(f"Network metrics: {metrics}")
        return metrics

    def identify_key_contributors(
        self, top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Identify key contributors based on multiple metrics

        Args:
            top_n: Number of top contributors to return

        Returns:
            List of dictionaries with contributor info and scores
        """
        if not self.graph:
            raise ValueError("Graph not initialized. Call build_network first.")

        logger.info(f"Identifying top {top_n} key contributors...")

        # Get all metrics
        centrality = self.calculate_centrality_metrics()
        structural_holes = self.detect_structural_holes()

        # Calculate composite score
        contributors = []
        for node in self.graph.nodes:
            cent = centrality.get(node, {})
            sh = structural_holes.get(node, {})

            # Weighted composite score
            composite_score = (
                0.3 * cent.get("degree_centrality", 0.0)
                + 0.3 * cent.get("betweenness_centrality", 0.0)
                + 0.2 * cent.get("pagerank", 0.0)
                + 0.2 * sh.get("effective_size", 0.0)
            )

            contributors.append(
                {
                    "username": node,
                    "composite_score": composite_score,
                    "degree_centrality": cent.get("degree_centrality", 0.0),
                    "betweenness_centrality": cent.get("betweenness_centrality", 0.0),
                    "pagerank": cent.get("pagerank", 0.0),
                    "is_bridge": sh.get("is_bridge", False),
                    "constraint": sh.get("constraint", 1.0),
                }
            )

        # Sort by composite score
        contributors.sort(key=lambda x: x["composite_score"], reverse=True)

        top_contributors = contributors[:top_n]
        logger.info(f"Identified {len(top_contributors)} key contributors")

        return top_contributors

    def calculate_bus_factor(self, threshold: float = 0.5) -> int:
        """
        Calculate bus factor (minimum number of contributors whose absence would cripple the project)

        Args:
            threshold: Contribution threshold (0-1)

        Returns:
            Bus factor number
        """
        if not self.graph:
            raise ValueError("Graph not initialized. Call build_network first.")

        logger.info("Calculating bus factor...")

        # Use degree centrality as proxy for contribution
        centrality = eg.degree_centrality(self.graph)

        # Sort by centrality
        sorted_contributors = sorted(
            centrality.items(), key=lambda x: x[1], reverse=True
        )

        # Calculate cumulative contribution
        total_centrality = sum(centrality.values())
        cumulative = 0.0
        bus_factor = 0

        for _, cent in sorted_contributors:
            cumulative += cent
            bus_factor += 1
            if cumulative / total_centrality >= threshold:
                break

        logger.info(f"Bus factor: {bus_factor}")
        return bus_factor

    def export_network_data(self) -> Dict[str, Any]:
        """
        Export network data for visualization

        Returns:
            Dictionary with nodes and edges data
        """
        if not self.graph:
            raise ValueError("Graph not initialized. Call build_network first.")

        nodes = []
        for node in self.graph.nodes:
            nodes.append(
                {
                    "id": node,
                    "degree": self.graph.degree(node),
                }
            )

        edges = []
        for u, v, data in self.graph.edges(data=True):
            edges.append(
                {
                    "source": u,
                    "target": v,
                    "weight": data.get("weight", 1.0),
                }
            )

        return {"nodes": nodes, "edges": edges}
