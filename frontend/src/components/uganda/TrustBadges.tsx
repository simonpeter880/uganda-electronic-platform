"use client";

import { Shield, TruckIcon, RotateCcw, Award, Headset, CreditCard } from "lucide-react";

const badges = [
	{
		icon: Shield,
		title: "Genuine Products",
		description: "100% authentic electronics",
		color: "text-green-600 bg-green-50",
	},
	{
		icon: Award,
		title: "1-Year Warranty",
		description: "Full manufacturer warranty",
		color: "text-blue-600 bg-blue-50",
	},
	{
		icon: TruckIcon,
		title: "Fast Delivery",
		description: "To all Uganda districts",
		color: "text-purple-600 bg-purple-50",
	},
	{
		icon: RotateCcw,
		title: "7-Day Returns",
		description: "Free & easy returns",
		color: "text-orange-600 bg-orange-50",
	},
	{
		icon: CreditCard,
		title: "Secure Payment",
		description: "MTN & Airtel Money",
		color: "text-yellow-600 bg-yellow-50",
	},
	{
		icon: Headset,
		title: "24/7 Support",
		description: "WhatsApp & SMS support",
		color: "text-pink-600 bg-pink-50",
	},
];

export default function TrustBadges() {
	return (
		<section className="py-12 bg-gray-50 rounded-3xl">
			<div className="container mx-auto px-4">
				<h2 className="text-2xl md:text-3xl font-bold text-gray-900 text-center mb-8">
					Why Shop With Us?
				</h2>

				<div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
					{badges.map((badge, index) => {
						const Icon = badge.icon;
						return (
							<div
								key={index}
								className="bg-white rounded-2xl p-6 text-center hover:shadow-card-hover transition-shadow"
							>
								<div
									className={`w-16 h-16 ${badge.color} rounded-full flex items-center justify-center mx-auto mb-4`}
								>
									<Icon size={32} strokeWidth={2} />
								</div>
								<h3 className="font-bold text-gray-900 mb-1">{badge.title}</h3>
								<p className="text-sm text-gray-600">{badge.description}</p>
							</div>
						);
					})}
				</div>
			</div>
		</section>
	);
}
