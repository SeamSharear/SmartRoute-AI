
import streamlit as st
import pandas as pd

from ortools.constraint_solver import (
    pywrapcp,
    routing_enums_pb2
)

# =====================================
# PAGE CONFIGURATION
# =====================================

st.set_page_config(
    page_title="SmartRoute AI",
    page_icon="🚚",
    layout="wide"
)

# =====================================
# SAMPLE LOCATIONS AND DISTANCES
# =====================================

locations = [
    "Delivery Hub",
    "Narail",
    "Lohagara",
    "Kalia",
    "Jessore",
    "Magura"
]

# Demonstration distances in kilometers.
# Replace with real Google Routes API data later.

distance_matrix = [
    [0, 12, 25, 31, 42, 55],
    [12, 0, 18, 24, 35, 48],
    [25, 18, 0, 15, 27, 39],
    [31, 24, 15, 0, 22, 33],
    [42, 35, 27, 22, 0, 19],
    [55, 48, 39, 33, 19, 0]
]

# =====================================
# ROUTE OPTIMIZATION FUNCTION
# =====================================

def optimize_route(matrix):

    n = len(matrix)

    manager = pywrapcp.RoutingIndexManager(
        n, 1, 0
    )

    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):

        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)

        return int(matrix[from_node][to_node])

    callback_index = routing.RegisterTransitCallback(
        distance_callback
    )

    routing.SetArcCostEvaluatorOfAllVehicles(
        callback_index
    )

    parameters = (
        pywrapcp.DefaultRoutingSearchParameters()
    )

    parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy
        .PATH_CHEAPEST_ARC
    )

    parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic
        .GUIDED_LOCAL_SEARCH
    )

    parameters.time_limit.seconds = 5

    solution = routing.SolveWithParameters(parameters)

    if solution is None:
        return None

    route = []
    index = routing.Start(0)

    while not routing.IsEnd(index):

        route.append(manager.IndexToNode(index))

        index = solution.Value(
            routing.NextVar(index)
        )

    route.append(manager.IndexToNode(index))

    return route


# =====================================
# DISTANCE CALCULATION
# =====================================

def calculate_distance(route, matrix):

    total = 0

    for i in range(len(route) - 1):

        total += matrix[
            route[i]
        ][
            route[i + 1]
        ]

    return total


# =====================================
# APPLICATION HEADER
# =====================================

st.title("🚚 SmartRoute AI")

st.subheader(
    "Smart Delivery Route Optimization System"
)

st.write(
    "Optimize your delivery sequence using "
    "Artificial Intelligence and Google OR-Tools."
)

st.divider()

# =====================================
# SIDEBAR
# =====================================

st.sidebar.title("SmartRoute AI")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Plan Delivery",
        "About"
    ]
)

# =====================================
# DASHBOARD
# =====================================

if page == "Dashboard":

    st.header("Dashboard")

    col1, col2, col3 = st.columns(3)

    col1.metric("Available Locations", len(locations))
    col2.metric("Vehicles", 1)
    col3.metric("Optimization Engine", "OR-Tools")

    st.info(
        "This is the initial development version. "
        "It uses sample distance data."
    )

    st.subheader("Available Delivery Locations")

    st.dataframe(
        pd.DataFrame({
            "Location": locations,
            "Location ID": range(len(locations))
        }),
        use_container_width=True,
        hide_index=True
    )


# =====================================
# PLAN DELIVERY
# =====================================

elif page == "Plan Delivery":

    st.header("📍 Plan Your Delivery")

    st.write("Starting location: **Delivery Hub**")

    selected = st.multiselect(
        "Select delivery destinations",
        options=locations[1:],
        default=locations[1:]
    )

    if st.button(
        "🚀 Optimize Route",
        type="primary"
    ):

        if not selected:

            st.warning(
                "Please select at least one destination."
            )

        else:

            indexes = [
                locations.index(x)
                for x in selected
            ]

            selected_indexes = [0] + indexes

            selected_names = [
                locations[i]
                for i in selected_indexes
            ]

            selected_matrix = [
                [
                    distance_matrix[i][j]
                    for j in selected_indexes
                ]
                for i in selected_indexes
            ]

            original_route = list(
                range(len(selected_names))
            ) + [0]

            optimized_route = optimize_route(
                selected_matrix
            )

            if optimized_route is None:

                st.error("Optimization failed.")

            else:

                original_distance = calculate_distance(
                    original_route,
                    selected_matrix
                )

                optimized_distance = calculate_distance(
                    optimized_route,
                    selected_matrix
                )

                saved = (
                    original_distance - optimized_distance
                )

                improvement = (
                    saved / original_distance * 100
                    if original_distance else 0
                )

                st.success("Optimization completed!")

                st.divider()

                c1, c2, c3 = st.columns(3)

                c1.metric(
                    "Original Distance",
                    f"{original_distance} km"
                )

                c2.metric(
                    "Optimized Distance",
                    f"{optimized_distance} km"
                )

                c3.metric(
                    "Distance Saved",
                    f"{saved} km",
                    f"{improvement:.2f}%"
                )

                st.subheader(
                    "Optimized Delivery Sequence"
                )

                for step, index in enumerate(
                    optimized_route
                ):

                    if step == 0:
                        label = "START"
                    elif step == len(optimized_route) - 1:
                        label = "RETURN"
                    else:
                        label = f"STOP {step}"

                    st.write(
                        f"**{label}:** {selected_names[index]}"
                    )

                st.subheader("Route Comparison")

                original_names = [
                    selected_names[i]
                    for i in original_route
                ]

                optimized_names = [
                    selected_names[i]
                    for i in optimized_route
                ]

                result = pd.DataFrame({
                    "Original Route": original_names,
                    "Optimized Route": optimized_names
                })

                st.dataframe(
                    result,
                    use_container_width=True,
                    hide_index=True
                )

                chart = pd.DataFrame({
                    "Route": ["Original", "Optimized"],
                    "Distance": [
                        original_distance,
                        optimized_distance
                    ]
                })

                st.subheader("Distance Analysis")

                st.bar_chart(
                    chart,
                    x="Route",
                    y="Distance"
                )


# =====================================
# ABOUT PAGE
# =====================================

elif page == "About":

    st.header("About SmartRoute AI")

    st.write("""
    SmartRoute AI is a delivery route optimization
    application.

    It uses the Traveling Salesperson Problem (TSP)
    and Google OR-Tools to find an efficient delivery
    sequence.

    The current version uses sample distance data.

    Future features:
    - Google Maps integration
    - Real road distance calculation
    - Multiple delivery vehicles
    - Delivery history
    - Route analytics
    """)

st.divider()

st.caption(
    "SmartRoute AI | AI Lab Project | Version 1.0"
)
