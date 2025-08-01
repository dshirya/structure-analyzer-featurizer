from cifkit import Cif
from cifkit.coordination.geometry import compute_polyhedron_metrics
from cifkit.utils import string_parser
from scipy.spatial import ConvexHull

from SAF.utils.element_order import get_binary_AB_elements, get_quaternary_ABCD_elements, get_ternary_RMX_elements


def get_CN_metrics_per_method(cif: Cif):
    """Find the best polyhedron for each label based on the minimum
    distance between the reference atom to the average position of
    connected atoms."""
    max_gaps_per_label = cif.CN_max_gap_per_site
    connections = cif.connections
    site_data = {}
    for label, CN_data_per_method in max_gaps_per_label.items():
        site_data[label] = {}
        for method, CN_data in CN_data_per_method.items():
            connection_data = connections[label][: CN_data["CN"]]
            polyhedron_points = []
            # Only if there are 4 or more points in the polyhedron
            if len(connection_data) > 3:
                for connection in connection_data:
                    polyhedron_points.append(connection[3])
            else:
                continue
            # Add the central atom as the last element
            polyhedron_points.append(connection_data[0][2])
            # Try to make a polyhedron
            try:
                hull = ConvexHull(polyhedron_points)
            except Exception:
                print(f"Error in determining polyhedron for {label} using {method} - skipped")
                site_data[label][method] = None
                continue  # Move to the next method
            # Returns none if there is any error
            polyhedron_metrics = compute_polyhedron_metrics(polyhedron_points, hull)
            site_data[label][method] = polyhedron_metrics
    return site_data


def _compute_number_of_atoms_in_binary_CN(label_connections, CN_metrics, A, B):
    """Compute the number of A, B atoms for each label, and 4 methods
    per label."""
    CN_atom_count_data = {}
    for site_label, method_data in CN_metrics.items():
        CN_atom_count_data[site_label] = {}
        for method, data in method_data.items():
            # Get the number of CN per method
            CN = data["number_of_vertices"]
            CN_connections = label_connections[site_label][:CN]
            A_element_count = 0
            B_element_count = 0
            for connection in CN_connections:
                connected_label = connection[0]
                parsed_label = string_parser.get_atom_type_from_label(connected_label)
                if parsed_label == A:
                    A_element_count += 1
                elif parsed_label == B:
                    B_element_count += 1
            CN_atom_count_data[site_label][method] = {
                "A_count": A_element_count,
                "B_count": B_element_count,
            }
    return CN_atom_count_data


def _compute_number_of_atoms_in_ternary_CN(label_connections, CN_metrics, R, M, X):
    """Compute the number of R, M, X atoms for each label, and 4 methods
    per label."""
    CN_atom_count_data = {}
    for site_label, method_data in CN_metrics.items():
        CN_atom_count_data[site_label] = {}
        for method, data in method_data.items():
            # Get the number of CN per method
            CN = data["number_of_vertices"]
            CN_connections = label_connections[site_label][:CN]
            R_element_count = 0
            M_element_count = 0
            X_element_count = 0
            for connection in CN_connections:
                connected_label = connection[0]
                parsed_label = string_parser.get_atom_type_from_label(connected_label)
                if parsed_label == R:
                    R_element_count += 1
                elif parsed_label == M:
                    M_element_count += 1
                elif parsed_label == X:
                    X_element_count += 1
            CN_atom_count_data[site_label][method] = {
                "R_count": R_element_count,
                "M_count": M_element_count,
                "X_count": X_element_count,
            }
    return CN_atom_count_data


def _compute_number_of_atoms_in_quaternary_CN(label_connections, CN_metrics, A, B, C, D):
    """Compute the number of A, B, C, D atoms for each label, and 4
    methods per label."""
    CN_atom_count_data = {}
    for site_label, method_data in CN_metrics.items():
        CN_atom_count_data[site_label] = {}
        for method, data in method_data.items():
            # Get the number of CN per method
            CN = data["number_of_vertices"]
            CN_connections = label_connections[site_label][:CN]
            A_element_count = 0
            B_element_count = 0
            C_element_count = 0
            D_element_count = 0
            for connection in CN_connections:
                connected_label = connection[0]
                parsed_label = string_parser.get_atom_type_from_label(connected_label)
                if parsed_label == A:
                    A_element_count += 1
                elif parsed_label == B:
                    B_element_count += 1
                elif parsed_label == C:
                    C_element_count += 1
                elif parsed_label == D:
                    D_element_count += 1
            CN_atom_count_data[site_label][method] = {
                "A_count": A_element_count,
                "B_count": B_element_count,
                "C_count": C_element_count,
                "D_count": D_element_count,
            }
    return CN_atom_count_data


def _compute_min_max_avg_per_atomic_label(site_data):
    """Calculate the minimum, maximum, and average of the 4 methods for
    each atomic site label, e.g., "Sb1", "Sb2"."""
    min_max_avg_per_site = {}
    # Iterate over each element (like Sb1, Th1, etc.)
    for label in site_data:
        metrics = {}
        # Iterate over each method under the element
        for method in site_data[label]:
            # Collect data for each metric within the method
            for key in site_data[label][method]:
                if key not in metrics:
                    metrics[key] = []
                metrics[key].append(site_data[label][method][key])
        # Calculate min, max, and avg for each metric within the site label
        min_max_avg_per_site[label] = {}
        for key in metrics:
            min_max_avg_per_site[label][key] = {
                "min": min(metrics[key]),
                "max": max(metrics[key]),
                "avg": sum(metrics[key]) / len(metrics[key]),
            }
    return min_max_avg_per_site


def _compute_global_avg_for_min_max_avg_metrics(min_max_avg_result):
    """Calculate global averages of all minimums, maximums, and averages
    across all labels from a pre-computed min-max-avg result.

    From the above function, we copmuted the min, max, and avg for each
    label, now we compute the global averages across all labels. This is
    important for ML since we are trying capture the global min, max,
    and avg of the coordination environment values.
    """
    global_sums = {"min": {}, "max": {}, "avg": {}}
    global_counts = {"min": {}, "max": {}, "avg": {}}
    # Summing values across all labels
    for label_data in min_max_avg_result.values():
        for metric, values in label_data.items():
            for stat in ["min", "max", "avg"]:
                if metric not in global_sums[stat]:
                    global_sums[stat][metric] = 0
                    global_counts[stat][metric] = 0
                global_sums[stat][metric] += values[stat]
                global_counts[stat][metric] += 1
    # Calculating global averages
    global_avg = {"min": {}, "max": {}, "avg": {}}
    for stat in ["min", "max", "avg"]:
        for metric, sum_value in global_sums[stat].items():
            global_avg[stat][metric] = float(sum_value / global_counts[stat][metric])
    return global_avg


def get_CN_atom_count_data(cif: Cif):
    # Compute geometrical features for the CN
    CN_metrics = get_CN_metrics_per_method(cif)
    # Compute min, max, and avg for each site label
    min_max_avg_CN_metrics = _compute_min_max_avg_per_atomic_label(CN_metrics)
    if len(cif.unique_elements) == 2:
        A, B = get_binary_AB_elements(list(cif.unique_elements))
        CN_atom_count_data = _compute_number_of_atoms_in_binary_CN(cif.connections, CN_metrics, A, B)
    if len(cif.unique_elements) == 3:
        R, M, X = get_ternary_RMX_elements(list(cif.unique_elements))
        CN_atom_count_data = _compute_number_of_atoms_in_ternary_CN(cif.connections, CN_metrics, R, M, X)
    if len(cif.unique_elements) == 4:
        A, B, C, D = get_quaternary_ABCD_elements(list(cif.unique_elements))
        CN_atom_count_data = _compute_number_of_atoms_in_quaternary_CN(cif.connections, CN_metrics, A, B, C, D)
    # Compute the min, max, and avg for each label. Each label has 4 methods
    min_max_avg_CN_count = _compute_min_max_avg_per_atomic_label(CN_atom_count_data)
    # Find the average of the min, max, and avg from
    avg_CN_metrics = _compute_global_avg_for_min_max_avg_metrics(min_max_avg_CN_metrics)
    avg_CN_atom_count = _compute_global_avg_for_min_max_avg_metrics(min_max_avg_CN_count)
    return avg_CN_metrics, avg_CN_atom_count
