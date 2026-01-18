"use client";

import { useState } from "react";
import Image from "next/image";
import {
	Star,
	Heart,
	Share2,
	TruckIcon,
	Shield,
	Clock,
	ChevronRight,
	ChevronDown,
	ChevronUp,
	Check,
	Plus,
	Minus,
	ShoppingCart,
	MapPin,
} from "lucide-react";
import ProductCard from "@/components/uganda/ProductCard";
import MobileMoneyPayment from "@/components/uganda/MobileMoneyPayment";
import DistrictSelector from "@/components/uganda/DistrictSelector";
import { mockFeaturedProducts, mockDistricts } from "@/lib/mock-data";

// Mock product detail (in real app, fetch from API)
const productDetail = {
	id: "1",
	name: "iPhone 14 Pro 128GB Deep Purple",
	slug: "iphone-14-pro-128gb",
	price: 4500000,
	originalPrice: 5200000,
	images: [
		"https://images.unsplash.com/photo-1678652197831-2d180705cd2c?w=800&q=80",
		"https://images.unsplash.com/photo-1678685888221-4e1cc0453e77?w=800&q=80",
		"https://images.unsplash.com/photo-1678652197821-99f9db48e3d2?w=800&q=80",
		"https://images.unsplash.com/photo-1678652197812-d4d4e9e89c14?w=800&q=80",
	],
	rating: 4.9,
	reviewCount: 234,
	stockCount: 3,
	soldToday: 12,
	deliveryFee: 10000,
	brand: "Apple",
	condition: "New",
	warranty: "1 Year International Warranty",
	specifications: [
		{ label: "Display", value: "6.1-inch Super Retina XDR display" },
		{ label: "Processor", value: "A16 Bionic chip" },
		{ label: "Camera", value: "48MP Main | 12MP Ultra Wide | 12MP Telephoto" },
		{ label: "Storage", value: "128GB" },
		{ label: "RAM", value: "6GB" },
		{ label: "Battery", value: "3200mAh with MagSafe charging" },
		{ label: "5G", value: "Yes" },
		{ label: "Face ID", value: "Yes" },
		{ label: "Water Resistance", value: "IP68 (6m for 30 minutes)" },
	],
	description: `The iPhone 14 Pro introduces a new way to interact with iPhone with Dynamic Island, a magical new experience that bubbles up alerts, notifications, and activities. It features an Always-On display, a more advanced camera system, and the fastest chip ever in a smartphone.

<strong>What's in the Box:</strong>
- iPhone 14 Pro
- USB-C to Lightning Cable
- Documentation

<strong>Why Buy from Us:</strong>
- 100% Genuine Apple Product
- 1-Year International Warranty
- Free Delivery to all Uganda Districts
- Pay with MTN/Airtel Mobile Money
- Flexible installment plans available`,
	highlights: [
		"Dynamic Island - A magical new way to interact with iPhone",
		"Always-On display - Your Lock Screen is always glanceable",
		"48MP Main camera for up to 4x resolution",
		"Cinematic mode now in 4K Dolby Vision at 30 fps",
		"Action mode for smooth, steady, handheld videos",
		"All-day battery life and up to 23 hours of video playback",
	],
};

const relatedProducts = mockFeaturedProducts.slice(0, 4).map((p) => ({
	...p,
	installmentPrice: Math.round(p.price / 3),
}));

export default function ProductDetailPage() {
	const [selectedImage, setSelectedImage] = useState(0);
	const [quantity, setQuantity] = useState(1);
	const [showSpecsAll, setShowSpecsAll] = useState(false);
	const [showPayment, setShowPayment] = useState(false);
	const [isWishlisted, setIsWishlisted] = useState(false);
	const [selectedDistrict, setSelectedDistrict] = useState(mockDistricts[0]);

	const installmentPrice = Math.round(productDetail.price / 3);
	const totalPrice = productDetail.price * quantity;
	const savingsAmount = productDetail.originalPrice
		? (productDetail.originalPrice - productDetail.price) * quantity
		: 0;

	const formatPrice = (amount: number) => {
		return new Intl.NumberFormat("en-UG", {
			style: "currency",
			currency: "UGX",
			minimumFractionDigits: 0,
			maximumFractionDigits: 0,
		}).format(amount);
	};

	const handleAddToCart = () => {
		// In real app, add to cart state/API
		alert(`Added ${quantity}x ${productDetail.name} to cart!`);
	};

	const handleBuyNow = () => {
		setShowPayment(true);
	};

	return (
		<div className="min-h-screen bg-gray-50">
			<div className="container mx-auto px-4 py-4">
				{/* Breadcrumbs */}
				<nav className="flex items-center gap-2 text-sm text-gray-600 mb-4">
					<a href="/" className="hover:text-primary-500 transition-colors">
						Home
					</a>
					<ChevronRight size={14} />
					<a href="/products" className="hover:text-primary-500 transition-colors">
						Products
					</a>
					<ChevronRight size={14} />
					<span className="text-gray-900 font-medium truncate">
						{productDetail.name}
					</span>
				</nav>

				<div className="grid lg:grid-cols-2 gap-6 mb-8">
					{/* Image Gallery */}
					<div className="space-y-3">
						{/* Main Image */}
						<div className="relative aspect-square bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
							<Image
								src={productDetail.images[selectedImage]}
								alt={productDetail.name}
								fill
								className="object-contain p-8"
								priority
							/>

							{/* Flash Deal Badge */}
							{productDetail.originalPrice && (
								<div className="absolute top-3 left-3 bg-primary-500 text-white px-3 py-1.5 rounded-full text-sm font-bold shadow-md">
									-
									{Math.round(
										((productDetail.originalPrice - productDetail.price) /
											productDetail.originalPrice) *
											100
									)}
									% OFF
								</div>
							)}

							{/* Wishlist Button */}
							<button
								onClick={() => setIsWishlisted(!isWishlisted)}
								className="absolute top-3 right-3 w-10 h-10 bg-white rounded-full shadow-md flex items-center justify-center hover:scale-110 transition-transform"
							>
								<Heart
									size={20}
									className={
										isWishlisted
											? "fill-error-500 text-error-500"
											: "text-gray-600"
									}
								/>
							</button>

							{/* Stock Badge */}
							{productDetail.stockCount <= 5 && (
								<div className="absolute bottom-3 left-3 bg-accent-500 text-white px-3 py-1.5 rounded-full text-sm font-semibold shadow-md">
									Only {productDetail.stockCount} left!
								</div>
							)}
						</div>

						{/* Thumbnail Gallery */}
						<div className="grid grid-cols-4 gap-2">
							{productDetail.images.map((image, index) => (
								<button
									key={index}
									onClick={() => setSelectedImage(index)}
									className={`relative aspect-square bg-white rounded-lg overflow-hidden transition-all border-2 ${
										selectedImage === index
											? "border-primary-500"
											: "border-gray-200 hover:border-gray-300"
									}`}
								>
									<Image
										src={image}
										alt={`${productDetail.name} ${index + 1}`}
										fill
										className="object-contain p-2"
									/>
								</button>
							))}
						</div>
					</div>

					{/* Product Info */}
					<div className="space-y-4">
						{/* Header */}
						<div>
							<div className="flex items-center gap-2 mb-2">
								<span className="text-xs font-semibold text-primary-500 bg-primary-50 px-2.5 py-1 rounded-full">
									{productDetail.brand}
								</span>
								<span className="text-xs font-semibold text-success-600 bg-success-50 px-2.5 py-1 rounded-full">
									{productDetail.condition}
								</span>
							</div>
							<h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-3">
								{productDetail.name}
							</h1>

							{/* Rating */}
							<div className="flex items-center gap-4 mb-4">
								<div className="flex items-center gap-1">
									{[...Array(5)].map((_, i) => (
										<Star
											key={i}
											size={20}
											className={
												i < Math.floor(productDetail.rating)
													? "fill-success-500 text-success-500"
													: "text-gray-300"
											}
										/>
									))}
									<span className="ml-2 text-lg font-bold text-gray-900">
										{productDetail.rating}
									</span>
								</div>
								<span className="text-gray-600">
									({productDetail.reviewCount} reviews)
								</span>
								<span className="text-accent-600 font-medium">
									{productDetail.soldToday} sold today
								</span>
							</div>
						</div>

						{/* Price */}
						<div className="bg-gradient-to-br from-primary-50 to-accent-50 rounded-xl p-5">
							<div className="flex items-baseline gap-3 mb-2">
								<span className="text-3xl md:text-4xl font-bold text-primary-500">
									{formatPrice(productDetail.price)}
								</span>
								{productDetail.originalPrice && (
									<span className="text-lg text-gray-400 line-through">
										{formatPrice(productDetail.originalPrice)}
									</span>
								)}
							</div>
							{savingsAmount > 0 && (
								<p className="text-success-600 font-semibold text-sm mb-2">
									You save {formatPrice(savingsAmount)}!
								</p>
							)}
							<p className="text-gray-700 text-sm">
								Or pay {formatPrice(installmentPrice)}/month for 3 months
							</p>
						</div>

						{/* Delivery */}
						<div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 space-y-3">
							<h3 className="font-bold text-gray-900 text-sm flex items-center gap-2">
								<TruckIcon size={18} className="text-primary-500" />
								Delivery Information
							</h3>
							<DistrictSelector
								districts={mockDistricts}
								selectedDistrict={selectedDistrict}
								onSelect={setSelectedDistrict}
							/>
							<div className="flex items-center gap-2 text-gray-700 text-sm">
								<Clock size={16} />
								<span>Delivered in {selectedDistrict.estimatedDays} days</span>
							</div>
						</div>

						{/* Quantity & Actions */}
						<div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 space-y-4">
							{/* Quantity Selector */}
							<div className="flex items-center gap-4">
								<span className="font-medium text-gray-700">Quantity:</span>
								<div className="flex items-center gap-3">
									<button
										onClick={() => setQuantity(Math.max(1, quantity - 1))}
										disabled={quantity <= 1}
										className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
									>
										<Minus size={20} />
									</button>
									<span className="w-12 text-center font-bold text-xl">
										{quantity}
									</span>
									<button
										onClick={() =>
											setQuantity(
												Math.min(productDetail.stockCount, quantity + 1)
											)
										}
										disabled={quantity >= productDetail.stockCount}
										className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
									>
										<Plus size={20} />
									</button>
								</div>
								<span className="text-sm text-gray-600">
									({productDetail.stockCount} available)
								</span>
							</div>

							{/* Action Buttons */}
							<div className="flex gap-2">
								<button
									onClick={handleBuyNow}
									className="flex-1 bg-accent-500 text-white py-3 rounded-full font-bold hover:bg-accent-600 transition-colors shadow-md"
								>
									Buy Now
								</button>
								<button
									onClick={handleAddToCart}
									className="flex-1 bg-primary-500 text-white py-3 rounded-full font-bold hover:bg-primary-600 transition-colors shadow-md flex items-center justify-center gap-2"
								>
									<ShoppingCart size={20} />
									Add to Cart
								</button>
							</div>

							<button className="w-full border-2 border-gray-200 text-gray-700 py-2.5 rounded-full font-medium hover:border-primary-500 hover:text-primary-500 transition-colors flex items-center justify-center gap-2">
								<Share2 size={18} />
								Share Product
							</button>
						</div>

						{/* Trust Badges */}
						<div className="grid grid-cols-2 gap-4">
							<div className="bg-white rounded-xl shadow-sm p-4 flex items-center gap-3">
								<Shield size={24} className="text-success-600" />
								<div>
									<p className="font-bold text-gray-900 text-sm">
										100% Genuine
									</p>
									<p className="text-xs text-gray-600">Verified product</p>
								</div>
							</div>
							<div className="bg-white rounded-xl shadow-sm p-4 flex items-center gap-3">
								<Check size={24} className="text-primary-600" />
								<div>
									<p className="font-bold text-gray-900 text-sm">
										{productDetail.warranty}
									</p>
									<p className="text-xs text-gray-600">Full coverage</p>
								</div>
							</div>
						</div>
					</div>
				</div>

				{/* Product Details Tabs */}
				<div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-8">
					{/* Description */}
					<div className="mb-6">
						<h2 className="text-xl font-bold text-gray-900 mb-3">
							Description
						</h2>
						<div
							className="prose prose-lg max-w-none text-gray-700"
							dangerouslySetInnerHTML={{ __html: productDetail.description }}
						/>
					</div>

					{/* Highlights */}
					<div className="mb-6">
						<h2 className="text-xl font-bold text-gray-900 mb-3">
							Key Features
						</h2>
						<ul className="space-y-3">
							{productDetail.highlights.map((highlight, index) => (
								<li key={index} className="flex items-start gap-3">
									<Check size={24} className="text-success-600 flex-shrink-0 mt-0.5" />
									<span className="text-gray-700">{highlight}</span>
								</li>
							))}
						</ul>
					</div>

					{/* Specifications */}
					<div>
						<div className="flex items-center justify-between mb-3">
							<h2 className="text-xl font-bold text-gray-900">
								Specifications
							</h2>
							<button
								onClick={() => setShowSpecsAll(!showSpecsAll)}
								className="text-primary-500 font-medium text-sm flex items-center gap-1 hover:text-primary-600"
							>
								{showSpecsAll ? "Show Less" : "Show All"}
								{showSpecsAll ? (
									<ChevronUp size={18} />
								) : (
									<ChevronDown size={18} />
								)}
							</button>
						</div>
						<div className="grid md:grid-cols-2 gap-4">
							{productDetail.specifications
								.slice(0, showSpecsAll ? undefined : 6)
								.map((spec, index) => (
									<div
										key={index}
										className="flex justify-between items-center bg-gray-50 rounded-xl p-4"
									>
										<span className="font-medium text-gray-700">
											{spec.label}
										</span>
										<span className="text-gray-900 font-semibold">
											{spec.value}
										</span>
									</div>
								))}
						</div>
					</div>
				</div>

				{/* Related Products */}
				<div className="mb-8">
					<h2 className="text-2xl font-bold text-gray-900 mb-4">
						You May Also Like
					</h2>
					<div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
						{relatedProducts.map((product) => (
							<ProductCard key={product.id} {...product} />
						))}
					</div>
				</div>
			</div>

			{/* Payment Modal */}
			{showPayment && (
				<div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
					<div className="bg-white rounded-3xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
						<div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex items-center justify-between">
							<h2 className="text-2xl font-bold text-gray-900">
								Complete Your Purchase
							</h2>
							<button
								onClick={() => setShowPayment(false)}
								className="text-gray-500 hover:text-gray-700"
							>
								✕
							</button>
						</div>
						<div className="p-6">
							{/* Order Summary */}
							<div className="bg-gray-50 rounded-2xl p-6 mb-6">
								<h3 className="font-bold text-gray-900 mb-4">Order Summary</h3>
								<div className="space-y-2 text-sm">
									<div className="flex justify-between">
										<span className="text-gray-600">
											{productDetail.name} x{quantity}
										</span>
										<span className="font-medium">
											{formatPrice(totalPrice)}
										</span>
									</div>
									<div className="flex justify-between">
										<span className="text-gray-600">Delivery Fee</span>
										<span className="font-medium">
											{formatPrice(selectedDistrict.deliveryFee)}
										</span>
									</div>
									<div className="border-t border-gray-300 pt-2 mt-2 flex justify-between text-lg">
										<span className="font-bold">Total</span>
										<span className="font-bold text-primary-600">
											{formatPrice(
												totalPrice + selectedDistrict.deliveryFee
											)}
										</span>
									</div>
								</div>
							</div>

							{/* Payment Component */}
							<MobileMoneyPayment
								amount={totalPrice + selectedDistrict.deliveryFee}
								orderId={`ORD-${Date.now()}`}
								onSuccess={() => {
									alert("Payment successful!");
									setShowPayment(false);
								}}
								onError={(error) => {
									alert(`Payment failed: ${error}`);
								}}
							/>
						</div>
					</div>
				</div>
			)}
		</div>
	);
}
