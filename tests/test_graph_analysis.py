"""
Test graph analysis and network analyzer
"""
import pytest
from unittest.mock import Mock, patch
import easygraph as eg

from src.graph_analysis.network_analyzer import CollaborationNetworkAnalyzer


class TestCollaborationNetworkAnalyzer:
    """Test suite for collaboration network analyzer"""

    @pytest.fixture
    def analyzer(self):
        """Create network analyzer instance"""
        return CollaborationNetworkAnalyzer()

    def test_build_network(self, analyzer, sample_collaboration_data):
        """Test building collaboration network"""
        graph = analyzer.build_network(sample_collaboration_data)

        assert graph is not None
        assert analyzer.graph is not None
        assert analyzer.graph.number_of_nodes() == 5
        assert analyzer.graph.number_of_edges() == 6

    def test_build_network_with_weights(self, analyzer, sample_collaboration_data):
        """Test network building with edge weights"""
        graph = analyzer.build_network(sample_collaboration_data)

        # Check if edge weights are properly set
        edge_data = graph["user1"]["user2"]
        assert "weight" in edge_data
        assert edge_data["weight"] == 5.0

    def test_build_empty_network(self, analyzer):
        """Test building network with empty data"""
        graph = analyzer.build_network([])

        assert graph is not None
        assert graph.number_of_nodes() == 0
        assert graph.number_of_edges() == 0

    def test_calculate_centrality(self, analyzer, sample_collaboration_data):
        """Test centrality metrics calculation"""
        analyzer.build_network(sample_collaboration_data)
        centrality = analyzer.calculate_centrality()

        assert centrality is not None
        assert "user1" in centrality
        assert "degree" in centrality["user1"]
        assert "betweenness" in centrality["user1"]
        assert "closeness" in centrality["user1"]
        assert "pagerank" in centrality["user1"]

    def test_centrality_values_range(self, analyzer, sample_collaboration_data):
        """Test that centrality values are in valid ranges"""
        analyzer.build_network(sample_collaboration_data)
        centrality = analyzer.calculate_centrality()

        for user, metrics in centrality.items():
            assert metrics["degree"] >= 0
            assert 0 <= metrics["betweenness"] <= 1
            assert 0 <= metrics["closeness"] <= 1
            assert 0 <= metrics["pagerank"] <= 1

    def test_detect_structural_holes(self, analyzer, sample_collaboration_data):
        """Test structural hole detection"""
        analyzer.build_network(sample_collaboration_data)
        structural_holes = analyzer.detect_structural_holes()

        assert structural_holes is not None
        assert len(structural_holes) > 0

        for user, metrics in structural_holes.items():
            assert "constraint" in metrics
            assert "effective_size" in metrics
            assert 0 <= metrics["constraint"] <= 1
            assert metrics["effective_size"] >= 0

    def test_detect_communities(self, analyzer, sample_collaboration_data):
        """Test community detection"""
        analyzer.build_network(sample_collaboration_data)
        communities = analyzer.detect_communities()

        assert communities is not None
        assert len(communities) > 0

        # Check that all nodes are assigned to a community
        for node in analyzer.graph.nodes():
            assert node in communities

    def test_calculate_bus_factor(self, analyzer, sample_collaboration_data):
        """Test bus factor calculation"""
        analyzer.build_network(sample_collaboration_data)
        bus_factor = analyzer.calculate_bus_factor()

        assert bus_factor is not None
        assert isinstance(bus_factor, int)
        assert bus_factor >= 1

    def test_identify_key_contributors(self, analyzer, sample_collaboration_data):
        """Test key contributor identification"""
        analyzer.build_network(sample_collaboration_data)
        key_contributors = analyzer.identify_key_contributors(top_n=3)

        assert key_contributors is not None
        assert len(key_contributors) <= 3
        assert all(isinstance(user, str) for user in key_contributors)

    def test_network_with_duplicate_edges(self, analyzer):
        """Test network building with duplicate edges (weight accumulation)"""
        collab_data = [
            {"from": "user1", "to": "user2", "weight": 3.0, "timestamp": "2024-01-15"},
            {"from": "user1", "to": "user2", "weight": 2.0, "timestamp": "2024-01-16"},
        ]

        graph = analyzer.build_network(collab_data)

        # Weight should be accumulated
        edge_data = graph["user1"]["user2"]
        assert edge_data["weight"] == 5.0

    def test_network_with_self_loops(self, analyzer):
        """Test network building with self-loops"""
        collab_data = [
            {"from": "user1", "to": "user1", "weight": 1.0, "timestamp": "2024-01-15"},
            {"from": "user1", "to": "user2", "weight": 2.0, "timestamp": "2024-01-16"},
        ]

        graph = analyzer.build_network(collab_data)

        # Should handle self-loops
        assert graph.number_of_nodes() == 2

    def test_get_network_statistics(self, analyzer, sample_collaboration_data):
        """Test network statistics calculation"""
        analyzer.build_network(sample_collaboration_data)
        stats = analyzer.get_network_statistics()

        assert stats is not None
        assert "num_nodes" in stats
        assert "num_edges" in stats
        assert "density" in stats
        assert "avg_degree" in stats

        assert stats["num_nodes"] == 5
        assert stats["num_edges"] == 6

    def test_find_bridges(self, analyzer, sample_collaboration_data):
        """Test bridge edge identification"""
        analyzer.build_network(sample_collaboration_data)
        bridges = analyzer.find_bridges()

        assert bridges is not None
        assert isinstance(bridges, list)

    def test_calculate_clustering_coefficient(self, analyzer, sample_collaboration_data):
        """Test clustering coefficient calculation"""
        analyzer.build_network(sample_collaboration_data)
        clustering = analyzer.calculate_clustering_coefficient()

        assert clustering is not None

        for user, coef in clustering.items():
            assert 0 <= coef <= 1

    def test_network_without_initialization(self, analyzer):
        """Test operations on uninitialized network"""
        with pytest.raises(AttributeError):
            analyzer.calculate_centrality()

    def test_large_network_performance(self, analyzer):
        """Test performance with larger network"""
        # Create a larger collaboration dataset
        large_collab_data = []
        for i in range(100):
            for j in range(i + 1, min(i + 5, 100)):
                large_collab_data.append({
                    "from": f"user{i}",
                    "to": f"user{j}",
                    "weight": 1.0,          "timestamp": "2024-01-15"
                })

        graph = analyzer.build_network(large_collab_data)

        assert graph.number_of_nodes() == 100

        # Should complete without timeout
        centrality = analyzer.calculate_centrality()
        assert len(centrality) == 100
