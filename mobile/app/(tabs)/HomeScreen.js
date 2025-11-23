import {
    StyleSheet,
    Text,
    View,
    ScrollView,
    Image,
    TextInput,
    TouchableOpacity,
    FlatList,
    ActivityIndicator,
    RefreshControl,
} from 'react-native';
import React, { useState, useEffect } from 'react';
import { Feather, Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import Colors from '../../constant/Colors';
import CarCard from '../../components/CarCard';
import { categories } from '../../constant/DummyData';
import { router } from 'expo-router';
import ApiService from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

export default function HomeScreen() {
    const [selectedCategory, setSelectedCategory] = useState('Sedan');
    const [availableCars, setAvailableCars] = useState([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const { isAuthenticated } = useAuth();

    useEffect(() => {
        fetchVehicles();
    }, []);

    const fetchVehicles = async () => {
        try {
            setLoading(true);
            const vehicles = await ApiService.getVehicles({
                status: 'available',
                page: 1,
                limit: 20,
            });
            
            // Transform API response to match CarCard component expectations
            const transformedVehicles = vehicles.map((vehicle) => ({
                id: vehicle.id,
                name: `${vehicle.make} ${vehicle.model}`,
                location: vehicle.location,
                seats: vehicle.seats,
                price: `AED ${vehicle.price_per_day}/Day`,
                image: vehicle.images && vehicle.images.length > 0 
                    ? { uri: vehicle.images[0] } 
                    : require('../../assets/cars/car_1.png'),
                isFavorite: false,
                rating: vehicle.rating || 0,
            }));
            
            setAvailableCars(transformedVehicles);
        } catch (error) {
            console.error('Error fetching vehicles:', error);
            // Fallback to empty array on error
            setAvailableCars([]);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    const onRefresh = () => {
        setRefreshing(true);
        fetchVehicles();
    };

    const handleFavoritePress = (carId) => {
        setAvailableCars(prevCars =>
            prevCars.map(car =>
                car.id === carId ? { ...car, isFavorite: !car.isFavorite } : car
            )
        );
    };

    const handleBookPress = (car) => {
        router.push(`/Home/BookingDetailsScreen?carId=${car.id}`);
    };

    const renderCategory = ({ item }) => (
        <TouchableOpacity
            style={styles.categoryItem}
            onPress={() => setSelectedCategory(item.name)}
        >
            <View
                style={[
                    styles.categoryImageContainer,
                    selectedCategory === item.name && styles.selectedCategory,
                ]}
            >
                <Image source={item.image} style={styles.categoryImage} resizeMode="contain" />
            </View>
            <Text style={styles.categoryText}>{item.name}</Text>
        </TouchableOpacity>
    );

    const renderCarCard = ({ item, index }) => (
        <CarCard
            item={item}
            index={index}
            onFavoritePress={handleFavoritePress}
            onBookPress={handleBookPress}
        />
    );

    if (loading && availableCars.length === 0) {
        return (
            <SafeAreaView style={styles.container} edges={['top']}>
                <View style={styles.loadingContainer}>
                    <ActivityIndicator size="large" color={Colors.Primary} />
                    <Text style={styles.loadingText}>Loading vehicles...</Text>
                </View>
            </SafeAreaView>
        );
    }

    return (
        <SafeAreaView style={styles.container} edges={['top']}>
            <ScrollView
                style={styles.scrollView}
                showsVerticalScrollIndicator={false}
                contentContainerStyle={styles.scrollContent}
                refreshControl={
                    <RefreshControl
                        refreshing={refreshing}
                        onRefresh={onRefresh}
                        colors={[Colors.Primary]}
                    />
                }
            >
                {/* Header */}
                <View style={styles.header}>
                    <View style={styles.logoContainer}>
                        <Image
                            source={require('../../assets/icons/car_icon_2.png')}
                            style={styles.logo}
                            resizeMode="contain"
                        />
                    </View>
                    <View style={styles.headerRight}>
                        <TouchableOpacity style={styles.notificationButton}>
                            <Ionicons name="notifications-outline" size={24} color="#000" />
                            <View style={styles.notificationBadge}>
                                <Text style={styles.badgeText}>2</Text>
                            </View>
                        </TouchableOpacity>
                        <TouchableOpacity style={styles.profileButton}>
                            <Image
                                source={require('../../assets/images/profile.jpg')}
                                style={styles.profileImage}
                            />
                        </TouchableOpacity>
                    </View>
                </View>

                {/* Search Bar */}
                <View style={styles.searchContainer}>
                    <View style={styles.searchBar}>
                        <Feather name="search" size={20} color="#999" />
                        <TextInput
                            style={styles.searchInput}
                            placeholder="Search your dream car...."
                            placeholderTextColor="#999"
                        />
                    </View>
                    <TouchableOpacity style={styles.filterButton}>
                        <Feather name="sliders" size={20} color="#000" />
                    </TouchableOpacity>
                </View>

                {/* What are you looking for? */}
                <Text style={styles.sectionTitle}>What are you looking for?</Text>

                {/* Categories - Horizontal Scroll */}
                <FlatList
                    data={categories}
                    renderItem={renderCategory}
                    keyExtractor={(item) => item.id}
                    horizontal
                    showsHorizontalScrollIndicator={false}
                    contentContainerStyle={styles.categoriesContainer}
                />

                {/* Available Cars */}
                <View style={styles.sectionHeader}>
                    <Text style={styles.sectionTitle}>Available Cars</Text>
                    <TouchableOpacity>
                        <Text style={styles.viewAllText}>View All</Text>
                    </TouchableOpacity>
                </View>

                {/* Cars Grid */}
                {availableCars.length > 0 ? (
                    <FlatList
                        data={availableCars}
                        renderItem={renderCarCard}
                        keyExtractor={(item) => item.id}
                        numColumns={2}
                        scrollEnabled={false}
                        columnWrapperStyle={styles.carRow}
                    />
                ) : (
                    <View style={styles.emptyContainer}>
                        <Text style={styles.emptyText}>No vehicles available</Text>
                        <Text style={styles.emptySubtext}>Pull down to refresh</Text>
                    </View>
                )}

                {/* Nearby Section */}
                <View style={styles.sectionHeader}>
                    <Text style={styles.sectionTitle}>Nearby</Text>
                    <TouchableOpacity>
                        <Text style={styles.viewAllText}>View All</Text>
                    </TouchableOpacity>
                </View>

                {/* Nearby Car */}
                <View style={styles.nearbyCard}>
                    <Image
                        source={require('../../assets/cars/car_1.png')}
                        style={styles.nearbyImage}
                        resizeMode="contain"
                    />
                </View>

                {/* Bottom Spacing for Tab Bar */}
                <View style={styles.bottomSpacer} />
            </ScrollView>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#F5F5F5',
    },
    scrollView: {
        flex: 1,
    },
    scrollContent: {
        paddingBottom: 100,
    },
    header: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingHorizontal: 20,
        paddingVertical: 16,
        backgroundColor: '#FFFFFF',
        borderBottomWidth: 1,
        borderBottomColor: Colors.Border,
    },
    logoContainer: {
        width: 40,
        height: 40,
        borderRadius: 20,
        backgroundColor: '#000',
        justifyContent: 'center',
        alignItems: 'center',
    },
    logo: {
        width: 40,
        height: 40
    },
    headerRight: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 12,
    },
    notificationButton: {
        position: 'relative',
    },
    notificationBadge: {
        position: 'absolute',
        top: -4,
        right: -4,
        backgroundColor: '#FF0000',
        borderRadius: 10,
        width: 18,
        height: 18,
        justifyContent: 'center',
        alignItems: 'center',
    },
    badgeText: {
        color: '#FFF',
        fontSize: 10,
        fontWeight: 'bold',
    },
    profileButton: {
        width: 40,
        height: 40,
        borderRadius: 20,
        overflow: 'hidden',
    },
    profileImage: {
        width: '100%',
        height: '100%',
    },
    searchContainer: {
        flexDirection: 'row',
        paddingHorizontal: 20,
        paddingVertical: 16,
        gap: 12,
        backgroundColor: '#FFFFFF',
        alignItems: 'center',
    },
    searchBar: {
        flex: 1,
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#F5F5F5',
        borderRadius: 12,
        paddingHorizontal: 16,
        paddingVertical: 7,
        gap: 8,
    },
    searchInput: {
        flex: 1,
        fontSize: 14,
        color: '#000',
    },
    filterButton: {
        width: 52,
        height: 52,
        backgroundColor: '#F5F5F5',
        borderRadius: 25.5,
        justifyContent: 'center',
        alignItems: 'center',
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#000',
        paddingHorizontal: 20,
        marginTop: 20,
        marginBottom: 16,
    },
    categoriesContainer: {
        paddingHorizontal: 20,
        gap: 16,
    },
    categoryItem: {
        alignItems: 'center',
        marginRight: 16,
    },
    categoryImageContainer: {
        width: 70,
        height: 70,
        borderRadius: 35,
        backgroundColor: '#E0E0E0',
        justifyContent: 'center',
        alignItems: 'center',
        marginBottom: 8,
    },
    selectedCategory: {
        backgroundColor: '#D0D0D0',
        borderWidth: 2,
        borderColor: '#000',
    },
    categoryImage: {
        width: 50,
        height: 50,
    },
    categoryText: {
        fontSize: 12,
        color: '#000',
        fontWeight: '500',
    },
    sectionHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingHorizontal: 20,
        paddingLeft: 0,
        marginTop: 20,
        marginBottom: 7,
    },
    viewAllText: {
        fontSize: 14,
        color: '#666',
    },
    carRow: {
        paddingHorizontal: 20,
        gap: 12,
    },
    nearbyCard: {
        marginHorizontal: 20,
        borderRadius: 16,
        overflow: 'hidden',
        backgroundColor: '#FFFFFF',
    },
    nearbyImage: {
        width: '100%',
        height: 150,
    },
    bottomSpacer: {
        height: 20,
    },
    loadingContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    loadingText: {
        marginTop: 16,
        fontSize: 16,
        color: Colors.TextSecondary,
    },
    emptyContainer: {
        padding: 40,
        alignItems: 'center',
    },
    emptyText: {
        fontSize: 18,
        fontWeight: 'bold',
        color: Colors.TextPrimary,
        marginBottom: 8,
    },
    emptySubtext: {
        fontSize: 14,
        color: Colors.TextSecondary,
    },
});
