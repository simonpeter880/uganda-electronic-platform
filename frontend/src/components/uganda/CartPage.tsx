"use client";

import { useState } from "react";
import Image from "next/image";
import {
	ShoppingCart,
	Trash2,
	Plus,
	Minus,
	ChevronRight,
	TruckIcon,
	Tag,
	Lock,
} from "lucide-react";
import { mockFeaturedProducts, mockDistricts } from "@/lib/mock-data";
import DistrictSelector from "@/components/uganda/DistrictSelector";

// Mock cart items (in real app, from state/API)
const mockCartItems = [
	{
		id: "cart-1",
		product: mockFeaturedProducts[0],
		quantity: 1,
	},
	{
		id: "cart-2",
		product: mockFeaturedProducts[1],
		quantity: 2,
	},
];

interface CartItem {
	id: string;
	product: {
		id: string;
		name: string;
		price: number;
		image: string;
		deliveryFee?: number;
	};
	quantity: number;
}

export default function UgandaCartPage() {
	const [cartItems, setCartItems] = useState<CartItem[]>(mockCartItems);
	const [selectedDistrict, setSelectedDistrict] = useState(mockDistricts[0]);
	const [promoCode, setPromoCode] = useState("");
	const [promoApplied, setPromoApplied] = useState(false);

	const formatPrice = (amount: number) => {
		return new Intl.NumberFormat("en-UG", {
			style: "currency",
			currency: "UGX",
			minimumFractionDigits: 0,
			maximumFractionDigits: 0,
		}).format(amount);
	};

	const updateQuantity = (itemId: string, newQuantity: number) => {
		if (newQuantity < 1) return;
		setCartItems((items) =>
			items.map((item) =>
				item.id === itemId ? { ...item, quantity: newQuantity } : item
			)
		);
	};

	const removeItem = (itemId: string) => {
		setCartItems((items) => items.filter((item) => item.id !== itemId));
	};

	const applyPromoCode = () => {
		if (promoCode.trim()) {
			setPromoApplied(true);
			// In real app, validate promo code with API
		}
	};

	// Calculate totals
	const subtotal = cartItems.reduce(
		(sum, item) => sum + item.product.price * item.quantity,
		0
	);
	const deliveryFee = selectedDistrict.deliveryFee;
	const discount = promoApplied ? Math.round(subtotal * 0.1) : 0; // 10% mock discount
	const total = subtotal + deliveryFee - discount;

	if (cartItems.length === 0) {
		return (
			<div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
				<div className="text-center max-w-md">
					<div className="w-32 h-32 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
						<ShoppingCart size={64} className="text-gray-400" />
					</div>
					<h1 className="text-3xl font-bold text-gray-900 mb-4">
						Your Cart is Empty
					</h1>
					<p className="text-gray-600 mb-8">
						Looks like you haven't added any items to your cart yet. Start shopping to
						fill it up!
					</p>
					<a
						href="/products"
						className="inline-block bg-primary-600 text-white px-8 py-4 rounded-xl font-bold hover:bg-primary-700 transition-colors"
					>
						Start Shopping
					</a>
				</div>
			</div>
		);
	}

	return (
		<div className="min-h-screen bg-gray-50">
			<div className="container mx-auto px-4 py-4">
				{/* Breadcrumbs */}
				<nav className="flex items-center gap-2 text-sm text-gray-600 mb-4">
					<a href="/" className="hover:text-primary-500 transition-colors">
						Home
					</a>
					<ChevronRight size={14} />
					<span className="text-gray-900 font-medium">Shopping Cart</span>
				</nav>

				{/* Header */}
				<div className="mb-6">
					<h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-1">
						Shopping Cart
					</h1>
					<p className="text-gray-600 text-sm">{cartItems.length} items in your cart</p>
				</div>

				<div className="grid lg:grid-cols-3 gap-6">
					{/* Cart Items */}
					<div className="lg:col-span-2 space-y-3">
						{cartItems.map((item) => (
							<div
								key={item.id}
								className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 flex gap-4"
							>
								{/* Product Image */}
								<div className="relative w-32 h-32 flex-shrink-0 bg-gray-50 rounded-xl overflow-hidden">
									<Image
										src={item.product.image}
										alt={item.product.name}
										fill
										className="object-contain p-4"
									/>
								</div>

								{/* Product Info */}
								<div className="flex-1 flex flex-col justify-between">
									<div>
										<a
											href={`/products/${item.product.id}`}
											className="font-bold text-lg text-gray-900 hover:text-primary-600 transition-colors"
										>
											{item.product.name}
										</a>
										<p className="text-2xl font-bold text-primary-600 mt-2">
											{formatPrice(item.product.price)}
										</p>
									</div>

									<div className="flex items-center justify-between mt-4">
										{/* Quantity Selector */}
										<div className="flex items-center gap-3 bg-gray-100 rounded-xl p-1">
											<button
												onClick={() =>
													updateQuantity(item.id, item.quantity - 1)
												}
												disabled={item.quantity <= 1}
												className="w-8 h-8 flex items-center justify-center hover:bg-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
											>
												<Minus size={18} />
											</button>
											<span className="w-12 text-center font-bold">
												{item.quantity}
											</span>
											<button
												onClick={() =>
													updateQuantity(item.id, item.quantity + 1)
												}
												className="w-8 h-8 flex items-center justify-center hover:bg-white rounded-lg transition-colors"
											>
												<Plus size={18} />
											</button>
										</div>

										{/* Remove Button */}
										<button
											onClick={() => removeItem(item.id)}
											className="text-error-600 hover:text-error-700 font-medium flex items-center gap-2 transition-colors"
										>
											<Trash2 size={18} />
											Remove
										</button>
									</div>
								</div>

								{/* Item Total */}
								<div className="text-right">
									<p className="text-sm text-gray-600 mb-1">Subtotal</p>
									<p className="text-2xl font-bold text-gray-900">
										{formatPrice(item.product.price * item.quantity)}
									</p>
								</div>
							</div>
						))}
					</div>

					{/* Order Summary */}
					<div className="space-y-4">
						{/* Delivery District */}
						<div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
							<h3 className="font-bold text-gray-900 text-sm mb-3 flex items-center gap-2">
								<TruckIcon size={18} className="text-primary-500" />
								Delivery Location
							</h3>
							<DistrictSelector
								districts={mockDistricts}
								selectedDistrict={selectedDistrict}
								onSelect={setSelectedDistrict}
							/>
							<p className="text-sm text-gray-600 mt-3">
								Estimated delivery: {selectedDistrict.estimatedDays} days
							</p>
						</div>

						{/* Promo Code */}
						<div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
							<h3 className="font-bold text-gray-900 text-sm mb-3 flex items-center gap-2">
								<Tag size={18} className="text-accent-500" />
								Promo Code
							</h3>
							<div className="flex gap-2">
								<input
									type="text"
									value={promoCode}
									onChange={(e) => setPromoCode(e.target.value)}
									placeholder="Enter promo code"
									disabled={promoApplied}
									className="flex-1 px-3 py-2 border border-gray-300 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:bg-gray-100"
								/>
								<button
									onClick={applyPromoCode}
									disabled={promoApplied || !promoCode.trim()}
									className="px-5 py-2 bg-accent-500 text-white rounded-full text-sm font-semibold hover:bg-accent-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
								>
									Apply
								</button>
							</div>
							{promoApplied && (
								<p className="text-success-700 text-sm mt-2 font-medium">
									✓ Promo code applied! You saved {formatPrice(discount)}
								</p>
							)}
						</div>

						{/* Order Summary */}
						<div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
							<h3 className="font-bold text-gray-900 text-sm mb-3">Order Summary</h3>
							<div className="space-y-2 text-sm">
								<div className="flex justify-between text-gray-700">
									<span>Subtotal ({cartItems.length} items)</span>
									<span className="font-medium">{formatPrice(subtotal)}</span>
								</div>
								<div className="flex justify-between text-gray-700">
									<span>Delivery Fee</span>
									<span className="font-medium">
										{formatPrice(deliveryFee)}
									</span>
								</div>
								{discount > 0 && (
									<div className="flex justify-between text-success-700">
										<span>Discount</span>
										<span className="font-medium">
											-{formatPrice(discount)}
										</span>
									</div>
								)}
								<div className="border-t border-gray-200 pt-3 flex justify-between text-lg">
									<span className="font-bold">Total</span>
									<span className="font-bold text-primary-600">
										{formatPrice(total)}
									</span>
								</div>
							</div>

							<a
								href="/checkout"
								className="w-full mt-4 bg-accent-500 text-white py-3 rounded-full font-bold hover:bg-accent-600 transition-colors flex items-center justify-center gap-2 shadow-md"
							>
								Proceed to Checkout
								<ChevronRight size={20} />
							</a>

							<div className="mt-3 flex items-center justify-center gap-2 text-xs text-gray-600">
								<Lock size={14} />
								<span>Secure checkout powered by Mobile Money</span>
							</div>
						</div>

						{/* Trust Badges */}
						<div className="bg-gradient-to-br from-primary-50 to-accent-50 rounded-xl p-4">
							<h4 className="font-bold text-gray-900 mb-3">Why Shop With Us?</h4>
							<ul className="space-y-2 text-sm text-gray-700">
								<li className="flex items-center gap-2">
									<span className="text-success-600">✓</span>
									100% Genuine Products
								</li>
								<li className="flex items-center gap-2">
									<span className="text-success-600">✓</span>
									Free Delivery Available
								</li>
								<li className="flex items-center gap-2">
									<span className="text-success-600">✓</span>
									MTN & Airtel Money Accepted
								</li>
								<li className="flex items-center gap-2">
									<span className="text-success-600">✓</span>
									Flexible Payment Plans
								</li>
							</ul>
						</div>
					</div>
				</div>

				{/* Continue Shopping */}
				<div className="mt-8 text-center">
					<a
						href="/products"
						className="inline-flex items-center gap-2 text-primary-600 hover:text-primary-700 font-medium"
					>
						← Continue Shopping
					</a>
				</div>
			</div>
		</div>
	);
}
