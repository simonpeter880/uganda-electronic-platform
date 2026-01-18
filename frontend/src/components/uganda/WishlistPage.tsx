"use client";

import { useState } from "react";
import { Heart, Trash2, ShoppingCart, ChevronRight } from "lucide-react";
import ProductCard from "@/components/uganda/ProductCard";
import { mockFeaturedProducts } from "@/lib/mock-data";

// Mock wishlist items
const mockWishlistItems = [
	{ ...mockFeaturedProducts[0], installmentPrice: Math.round(mockFeaturedProducts[0].price / 3), addedDate: "2025-01-10" },
	{ ...mockFeaturedProducts[1], installmentPrice: Math.round(mockFeaturedProducts[1].price / 3), addedDate: "2025-01-08" },
	{ ...mockFeaturedProducts[2], installmentPrice: Math.round(mockFeaturedProducts[2].price / 3), addedDate: "2025-01-05" },
	{ ...mockFeaturedProducts[3], installmentPrice: Math.round(mockFeaturedProducts[3].price / 3), addedDate: "2025-01-03" },
];

export default function WishlistPage() {
	const [wishlistItems, setWishlistItems] = useState(mockWishlistItems);

	const formatPrice = (amount: number) => {
		return new Intl.NumberFormat("en-UG", {
			style: "currency",
			currency: "UGX",
			minimumFractionDigits: 0,
			maximumFractionDigits: 0,
		}).format(amount);
	};

	const removeFromWishlist = (itemId: string) => {
		setWishlistItems(items => items.filter(item => item.id !== itemId));
	};

	const addToCart = (itemId: string) => {
		// In real app, add to cart state/API
		alert("Added to cart!");
	};

	const totalValue = wishlistItems.reduce((sum, item) => sum + item.price, 0);

	if (wishlistItems.length === 0) {
		return (
			<div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
				<div className="text-center max-w-md">
					<div className="w-32 h-32 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
						<Heart size={64} className="text-gray-400" />
					</div>
					<h1 className="text-3xl font-bold text-gray-900 mb-4">
						Your Wishlist is Empty
					</h1>
					<p className="text-gray-600 mb-8">
						Save items you love to your wishlist. Start adding products now!
					</p>
					<a
						href="/products"
						className="inline-block bg-primary-600 text-white px-8 py-4 rounded-xl font-bold hover:bg-primary-700 transition-colors"
					>
						Browse Products
					</a>
				</div>
			</div>
		);
	}

	return (
		<div className="min-h-screen bg-gray-50">
			<div className="container mx-auto px-4 py-6">
				{/* Breadcrumbs */}
				<nav className="flex items-center gap-2 text-sm text-gray-600 mb-6">
					<a href="/" className="hover:text-primary-600 transition-colors">
						Home
					</a>
					<ChevronRight size={16} />
					<span className="text-gray-900 font-medium">Wishlist</span>
				</nav>

				{/* Header */}
				<div className="mb-8">
					<h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2 flex items-center gap-3">
						<Heart size={40} className="fill-error-500 text-error-500" />
						My Wishlist
					</h1>
					<p className="text-gray-600">
						{wishlistItems.length} items · Total value: {formatPrice(totalValue)}
					</p>
				</div>

				<div className="grid lg:grid-cols-4 gap-8">
					{/* Wishlist Items */}
					<div className="lg:col-span-3">
						<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
							{wishlistItems.map((item) => (
								<div key={item.id} className="relative">
									<ProductCard {...item} />
									{/* Remove Button Overlay */}
									<button
										onClick={() => removeFromWishlist(item.id)}
										className="absolute top-4 right-4 w-10 h-10 bg-white rounded-full shadow-lg flex items-center justify-center hover:bg-error-50 transition-colors z-10"
										title="Remove from wishlist"
									>
										<Trash2 size={20} className="text-error-600" />
									</button>
									{/* Add to Cart Button Overlay */}
									<button
										onClick={() => addToCart(item.id)}
										className="absolute bottom-4 left-4 right-4 bg-primary-600 text-white py-3 rounded-xl font-bold hover:bg-primary-700 transition-colors flex items-center justify-center gap-2 z-10"
									>
										<ShoppingCart size={20} />
										Add to Cart
									</button>
								</div>
							))}
						</div>
					</div>

					{/* Sidebar */}
					<div>
						<div className="bg-white rounded-2xl shadow-card p-6 sticky top-6">
							<h3 className="font-bold text-gray-900 mb-4">Wishlist Summary</h3>
							<div className="space-y-4 mb-6">
								<div className="flex justify-between text-sm">
									<span className="text-gray-600">Total Items</span>
									<span className="font-bold text-gray-900">{wishlistItems.length}</span>
								</div>
								<div className="flex justify-between">
									<span className="text-gray-600">Total Value</span>
									<span className="text-lg font-bold text-primary-600">
										{formatPrice(totalValue)}
									</span>
								</div>
							</div>

							<button
								onClick={() => {
									// In real app, add all to cart
									alert("All items added to cart!");
								}}
								className="w-full bg-accent-600 text-white py-4 rounded-xl font-bold hover:bg-accent-700 transition-colors mb-3"
							>
								Add All to Cart
							</button>

							<button
								className="w-full border-2 border-gray-300 text-gray-700 py-4 rounded-xl font-medium hover:border-primary-600 hover:text-primary-600 transition-colors"
								onClick={() => setWishlistItems([])}
							>
								Clear Wishlist
							</button>

							<div className="mt-6 bg-gradient-to-br from-primary-50 to-accent-50 rounded-xl p-4">
								<p className="text-sm text-gray-700">
									<strong>Tip:</strong> Items in your wishlist may go out of stock. Add them to cart to secure your purchase!
								</p>
							</div>
						</div>
					</div>
				</div>

				{/* Recommendations */}
				<div className="mt-12">
					<h2 className="text-2xl font-bold text-gray-900 mb-6">
						You May Also Like
					</h2>
					<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
						{mockFeaturedProducts.slice(4, 8).map((product) => (
							<ProductCard
								key={product.id}
								{...product}
								installmentPrice={Math.round(product.price / 3)}
							/>
						))}
					</div>
				</div>
			</div>
		</div>
	);
}
