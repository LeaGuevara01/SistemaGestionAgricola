import React from 'react';

const Card = ({ title, description, price, image }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      {image && <img src={image} alt={title} className="w-full h-32 object-cover rounded-t-lg" />}
      <h3 className="text-lg font-semibold mt-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
      <p className="text-green-600 font-bold mt-2">${price}</p>
    </div>
  );
};

export default Card;