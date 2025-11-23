import React, { useState, useRef } from "react";
import {
    View,
    StyleSheet,
    Text,
    StatusBar,
    ImageBackground,
    Dimensions,
    Image,
    FlatList,
    TouchableOpacity,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { LinearGradient } from "expo-linear-gradient";
import { router } from "expo-router";

import Colors from "../../constant/Colors";
import CustomeFonts from "../../constant/customeFonts";
import CustomButton from "../../components/CustomButton";

const { width, height } = Dimensions.get("window");

const onboardingData = [
    {
        id: 1,
        title: "Welcome to",
        subtitle: "Zoupash",
        description: "",
        backgroundImage: require("../../assets/background_images/background_1.png"),
    },
    {
        id: 2,
        title: "Lets Start A New Experience",
        subtitle: "With Car rental.",
        description: "Discover your next adventure with Qent. we're here to provide you with a seamless car rental experience. Let's get started on your journey.",
        backgroundImage: require("../../assets/background_images/background_2.png"),
    },
];

export default function OnboardingScreen() {
    const [currentIndex, setCurrentIndex] = useState(0);
    const flatListRef = useRef(null);
    const currentIndexRef = useRef(0); // Use ref for immediate access

    const onViewableItemsChanged = useRef(({ viewableItems }) => {
        if (viewableItems.length > 0) {
            const index = viewableItems[0].index;
            setCurrentIndex(index);
            currentIndexRef.current = index; // Update ref as well
        }
    }).current;

    const viewabilityConfig = useRef({
        itemVisiblePercentThreshold: 50,
    }).current;

    const handleNext = () => {
        // Use currentIndex state directly
        if (currentIndex < onboardingData.length - 1) {
            const nextIndex = currentIndex + 1;
            // Use scrollToOffset directly as it's more reliable
            flatListRef.current?.scrollToOffset({
                offset: nextIndex * width,
                animated: true,
            });
        } else {
            // Navigate to LoginScreen after last onboarding screen
            router.replace("/(Authentication)/LoginScreen");
        }
    };

    const renderOnboardingItem = ({ item, index }) => (
        <View style={styles.slideContainer}>
            <ImageBackground
                source={item.backgroundImage}
                style={styles.backgroundImage}
                resizeMode="cover"
            >
                <LinearGradient
                    colors={[
                        "rgba(0, 0, 0, 0.9)",
                        "rgba(0, 0, 0, 0.9)",
                        "rgba(0, 0, 0, 0.02)"
                    ]}
                    locations={[0, 0.497, 0.959]}
                    style={styles.gradientOverlay}
                >
                    <SafeAreaView style={styles.safeArea}>
                        {/* Header Section with Car Icon */}
                        <View style={styles.headerSection}>
                            <View style={styles.logoContainer}>
                                <View>
                                    <Image
                                        source={require("../../assets/icons/car_icon.png")}
                                        style={styles.carIcon}
                                        resizeMode="contain"
                                    />
                                </View>
                            </View>
                        </View>

                        {/* Main Content Section */}
                        <View style={styles.contentSection}>
                            <View style={styles.textContainer}>
                                <Text style={styles.titleText}>{item.title}</Text>
                                <Text style={styles.subtitleText}>{item.subtitle}</Text>
                            </View>
                        </View>

                        {/* Bottom Section */}
                        <View style={styles.bottomSection}>
                            {/* Description Text */}
                            {item.description ? (
                                <Text style={styles.descriptionText}>{item.description}</Text>
                            ) : null}

                            {/* Pagination Indicators */}
                            <View style={styles.paginationContainer} pointerEvents="none">
                                {onboardingData.map((_, idx) => (
                                    <View
                                        key={idx}
                                        style={[
                                            styles.paginationDot,
                                            index === idx && styles.activeDot
                                        ]}
                                    />
                                ))}
                            </View>
                        </View>
                    </SafeAreaView>
                </LinearGradient>
            </ImageBackground>
        </View>
    );

    return (
        <View style={styles.container}>
            <StatusBar barStyle="light-content" backgroundColor={Colors.Secondary} />

            <FlatList
                ref={flatListRef}
                data={onboardingData}
                renderItem={renderOnboardingItem}
                keyExtractor={(item) => item.id.toString()}
                horizontal
                pagingEnabled
                scrollEnabled={true}
                showsHorizontalScrollIndicator={false}
                onViewableItemsChanged={onViewableItemsChanged}
                viewabilityConfig={viewabilityConfig}
                getItemLayout={(data, index) => ({
                    length: width,
                    offset: width * index,
                    index,
                })}
                onScrollToIndexFailed={(info) => {
                    const wait = new Promise(resolve => setTimeout(resolve, 500));
                    wait.then(() => {
                        flatListRef.current?.scrollToIndex({ index: info.index, animated: true });
                    });
                }}
                nestedScrollEnabled={true}
            />

            {/* Button outside FlatList for better touch handling */}
            <View style={styles.externalButtonContainer}>
                <TouchableOpacity
                    activeOpacity={0.8}
                    onPress={handleNext}
                    style={[styles.button, styles.filledButton]}
                >
                    <Text style={styles.buttonText}>
                        {currentIndex === onboardingData.length - 1 ? "Get Started" : "Next"}
                    </Text>
                </TouchableOpacity>
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
    },
    slideContainer: {
        width: width,
        height: height,
    },
    backgroundImage: {
        flex: 1,
        width: width,
        height: height,
    },
    gradientOverlay: {
        flex: 1,
        borderRadius: 0,
    },
    safeArea: {
        flex: 1,
    },
    headerSection: {
        paddingTop: 60,
        paddingLeft: 30,
        paddingBottom: 20,
    },
    logoContainer: {
        alignItems: "flex-start",
    },
    logoCircle: {
        width: 80,
        height: 80,
        borderRadius: 40,
        backgroundColor: "rgba(255, 255, 255, 0.1)",
        justifyContent: "center",
        alignItems: "center",
        borderWidth: 2,
        borderColor: "rgba(255, 255, 255, 0.3)",
    },
    carIcon: {
        width: 50,
        height: 50,
    },
    contentSection: {
        paddingHorizontal: 30,
        paddingTop: 20,
        flex: 1,
    },
    textContainer: {
        alignItems: "flex-start",
    },
    titleText: {
        fontFamily: CustomeFonts.Gilroy_Light,
        fontSize: 32,
        color: Colors.White,
        textAlign: "left",
        marginBottom: 8,
        lineHeight: 38,
    },
    subtitleText: {
        fontFamily: CustomeFonts.Gilroy_ExtraBold,
        fontSize: 32,
        color: Colors.White,
        textAlign: "left",
        fontWeight: "bold",
        marginBottom: 16,
        lineHeight: 38,
    },
    descriptionText: {
        fontFamily: CustomeFonts.Lato_Regular,
        fontSize: 16,
        color: Colors.White,
        textAlign: "left",
        lineHeight: 24,
        opacity: 0.9,
        marginBottom: 30,
        paddingHorizontal: 0,
        alignSelf: "stretch",
    },
    bottomSection: {
        paddingHorizontal: 30,
        paddingBottom: 60,
        position: "absolute",
        bottom: 0,
        left: 0,
        right: 0,
        alignItems: "stretch",
    },
    paginationContainer: {
        flexDirection: "row",
        justifyContent: "center",
        alignItems: "center",
        marginBottom: 30,
    },
    paginationDot: {
        width: 8,
        height: 8,
        borderRadius: 4,
        backgroundColor: "rgba(255, 255, 255, 0.3)",
        marginHorizontal: 4,
    },
    activeDot: {
        backgroundColor: Colors.White,
        width: 12,
        height: 8,
        borderRadius: 4,
    },
    buttonWrapper: {
        marginTop: 10,
    },
    externalButtonContainer: {
        position: 'absolute',
        bottom: 60,
        left: 30,
        right: 30,
        zIndex: 10,
    },
    button: {
        borderRadius: 12,
        paddingVertical: 16,
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: 16,
    },
    filledButton: {
        backgroundColor: '#374151',
    },
    buttonText: {
        fontSize: 16,
        fontWeight: '600',
        color: '#FFFFFF',
    },
});
