import networkx as nx
import random

# Import G146 graph from gexf file
G146 = nx.read_gexf('graph_0146_01234.gexf', node_type=int)
#G500 = nx.read_gexf('graph_0500_01234.gexf', node_type=int)
rng = random.Random()

# Define Algorithm hyperparameters
total_nodes = 146
population = 140
half_pop = int(population / 2)
k = 13  # number of centers
mutation_rate = 0.2
max_generations = 200
max_epochs = 70
number_mutations = mutation_rate * population


def initialize_chromosomes():
    """
    Function that initializes the population and creates the chromosomes to be used in the genetic algorithm.
    """

    # fill each chromosome with zeros
    chromosomes = [[0]*total_nodes for x in range(population)]
    for i in range(population):
        # generate k random numbers from range 0-total_nodes, each one representing a city-center
        pos = random.sample(range(0, total_nodes), k)
        for j in pos:
            chromosomes[i][j] = 1

    return chromosomes


def k_centers_objective_value(Graph, centers):
    """
    Function that given a graph and a list of centers, calculates the score of this solution to the k-center problem.
    We define the score of a chromosome as the maximum distance between all nodes and their closest center
    """

    closest_center_distance = [0] * len(Graph)
    for i in Graph.nodes:
        minimum = 100000
        # if i node is a center
        if i in centers:
            closest_center_distance[i] = 0
        else:
            # Calculate the distance of every node to the centers and find the closest center
            for j in range(k):
                dist = Graph[i][centers[j]]['weight']
                if (dist < minimum):
                    minimum = dist
                    closest_center_distance[i] = dist

    # Find Max distance between node and its closest center
    obj_val = max(closest_center_distance)

    return obj_val


def fitness(Graph, chromosomes):
    """
     Fitness function calculates the score/'strength of each chromosome'
    """

    centers = [[] for i in range(population)]
    current_number_centers = [[0] for i in range(population)]
    score = [[0] for i in range(population)]

    # Calculate the number of centers each chromosome has, and keep centers in a 'centers' list
    for p in range(population):
        # Count the centers of each chromosome
        current_number_centers[p] = chromosomes[p][:].count(1)
        # And store them in 'centers' list
        for j in range(total_nodes):
            if chromosomes[p][j] == 1:
                centers[p].append(j)

    for i in range(population):
        # Make sure that the number of centers is always equal to  k. Crossover and mutation step can't guarantee that.
        while current_number_centers[i] != k:
            # In case a chromosome has more than k centers, randomly remove a center
            # In case a chromosome has less than k centers, randomly add a center
            if current_number_centers[i] > k:
                # randomly choose which center to remove
                rand_center = rng.randint(0, current_number_centers[i] - 1)
                # pop it out of the list
                center_pos = centers[i].pop(rand_center)
                # update the chromosome
                chromosomes[i][center_pos] = 0
            else:
                # randomly choose where to set the new center
                rand_center = rng.randint(0, total_nodes - 1)
                # check if the random center already exists in the centers list
                already_exists = 0
                while already_exists == 0:
                    if rand_center not in centers[i]:
                        already_exists = 1
                    else:
                        rand_center = rng.randint(0, total_nodes-1)
                # add it to the list
                centers[i].append(rand_center)
                # update the chromosome
                chromosomes[i][rand_center] = 1

            # Count the new number of centers
            current_number_centers[i] = chromosomes[i][:].count(1)

        # Call function that calculates the score based on the given graph
        score[i] = int(k_centers_objective_value(Graph, centers[i]))

    centers.clear()

    return score, chromosomes


def crossover(chromosomes):
    """
    Function that implements the crossover step. In this approach,The first best-half of the population is reproducing.
    Each pair of chromosomes gives 'birth' to two children, which are placed in the position of the second half of the
    population. The reproduction is done by choosing a random area from each parent and combining it with the rest,
    like this:

       Parent A: AAAAAAAAAAAAAAAA                    Child 1: AAABBBBAAAAAAAAA
                   ^--^              Results in ==>
       Parent B: BBBBBBBBBBBBBBBB                    Child 2: BBBAAAABBBBBBBBB

    After reproduction stage, The best 8 chromosomes survive intact to the next generation while the rest,
    are replaced with random chromosomes(re-initialized).
    """

    for i in range(0, half_pop, 2): # with step 2
        # Generate two random points in the range 0 to total_nodes. And make sure cross1 < cross2
        point1 = rng.randint(0, total_nodes - 1)
        point2 =rng.randint(0, total_nodes - 1)
        if point1>point2:
            # swap
            temp = point2
            point2 = point1
            point1 = temp

        # 1st child
        chromosomes[-1 - i][:] = chromosomes[i][:]
        chromosomes[-1 - i][point1 : (point2 + 1)] = chromosomes[i + 1][point1 : (point2+1)]
        # 2nd child
        chromosomes[-2 - i][:] = chromosomes[i + 1][:]
        chromosomes[-2 - i][point1 : (point2+1)] = chromosomes[i][point1 : (point2 + 1)]

    # Let the first 8 chromosomes intect, and reinitialize the rest 'parents'.
    for i in range(8, half_pop):
        # fill each chromosome with zeros
        for p in range(total_nodes):
            chromosomes[i][p] = 0
        # generate k random numbers from range 0-total_nodes, each one representing a city-center
        pos1 = random.sample(range(0, total_nodes), k)
        for j in pos1:
            chromosomes[i][j] = 1


def mutation(chromosomes):
    """
    Function that implements the mutation step. Flip the state of a random gene at a random chromosome.
    The number of mutations depends on the hyperparameter mutation_rate.
    """

    for n in range(int(number_mutations)):
        # choose a random chromosome
        xx = rng.randint(0, population - 1)
        # choose a random point
        yy = rng.randint(0, total_nodes - 1)
        # And flip it to 0 or 1, depending on its previous state
        chromosomes[xx][yy] = 1 - chromosomes[xx][yy]



def genetic_algorithm():
    """
    Main function that calls all the required steps for the genetic algorithm
    """

    # Initialization step
    chromosomes = initialize_chromosomes()
    previous_score = 0
    for generation in range(max_generations):
        # Calculate fitness score of every chromosome
        score, chromosomes = fitness(G146, chromosomes)

        # Sort chromosomes based on their fitness score and rearrange them
        index_and_scores = dict(zip(range(population), score))
        index_and_scores_sorted = sorted(index_and_scores.items(), key=lambda kv: kv[1])
        sorted_indexes = [i[0] for i in index_and_scores_sorted]
        index_and_chromosomes = dict(zip(range(population), chromosomes))
        # Rearrange chromosomes' order based on their score
        chromosomes = [index_and_chromosomes[i] for i in sorted_indexes]

        # Print the best chromosome and its score in this generation
        best_centers = []
        for j in range(total_nodes):
            if chromosomes[0][j] == 1:
                best_centers.append(j)
        print('Generation: ', generation, ' Cost: ', index_and_scores_sorted[0][1])
        print('Best solution: ', best_centers)
        print('Number of Centers: ', chromosomes[0][:].count(1))

        # Crossover step
        crossover(chromosomes)
        # Mutation step
        mutation(chromosomes)

        # Calculate the number of epochs that the best score hasn't changed
        if previous_score == index_and_scores_sorted[0][1]:
            epochs_unchanged = epochs_unchanged + 1
        else:
            epochs_unchanged = 1
        # Get the current score
        previous_score = index_and_scores_sorted[0][1]

        # If epochs_unchanged passes the Max_epochs limit, then finish the Algorithm
        if epochs_unchanged >= max_epochs:
            break

        # Clear lists for next generation
        score.clear()
        index_and_scores_sorted.clear()
        index_and_scores.clear()
        index_and_chromosomes.clear()



if __name__ == "__main__":
    genetic_algorithm()